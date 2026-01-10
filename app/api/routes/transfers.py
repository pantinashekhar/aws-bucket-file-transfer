from fastapi import APIRouter, Depends, HTTPException, Query , BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from uuid import uuid4
from db.session import get_session, AsyncSessionLocal
from db.models import TransferJob, OperationStatus
from storage.deps import get_storage_client
from storage.base import StorageClient
from fastapi import BackgroundTasks
from io import BytesIO

router = APIRouter(prefix="/transfers", tags=["transfers"])



@router.post("/")
async def create_transfer(
    source_bucket: str,
    source_key: str,
    dest_bucket: str,
    dest_key: str,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_session),
    storage: StorageClient = Depends(get_storage_client),
):
    if source_bucket == dest_bucket and source_key == dest_key:
        raise HTTPException(400, "Source and destination must differ")

    # Create pending job immediately
    job = TransferJob(
        job_id=str(uuid4())[:8],
        source_bucket=source_bucket,
        source_key=source_key,
        dest_bucket=dest_bucket,
        dest_key=dest_key,
        status=OperationStatus.PENDING
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)

    # Queue background processing
    background_tasks.add_task(perform_transfer, job.id, storage)
    
    return {
        "job_id": job.job_id,
        "status": "pending",
        "message": "Transfer queued - check status below"
    }


@router.get("/recent")
async def get_recent_jobs(
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(TransferJob).order_by(TransferJob.created_at.desc()).limit(5)
    )
    jobs = result.scalars().all()
    return [{
        "jobId": job.job_id,
        "status": job.status,
        "source": f"{job.source_bucket}/{job.source_key}",
        "dest": f"{job.dest_bucket}/{job.dest_key}",
    } for job in jobs]

@router.get("/{job_id}")
async def get_job_status(
    job_id: str,
    session: AsyncSession = Depends(get_session),
):
    result = await session.execute(
        select(TransferJob).where(TransferJob.job_id == job_id)
    )
    job = result.scalars().first()
    
    if not job:
        raise HTTPException(404, "Job not found")
    
    return {
        "jobId": job.job_id,
        "status": job.status,
        "source": f"{job.source_bucket}/{job.source_key}",
        "dest": f"{job.dest_bucket}/{job.dest_key}",
    }


async def perform_transfer(job_id: int, storage: StorageClient):
    """Background transfer worker"""
    session = AsyncSessionLocal()
    try:
        result = await session.execute(
            select(TransferJob).where(TransferJob.id == job_id)
        )
        job = result.scalar_one()
        
        job.status = OperationStatus.IN_PROGRESS
        await session.commit()
        
        # Copy file
        source_data = await storage.download_file(job.source_bucket, job.source_key)
        await storage.upload_file(job.dest_bucket, job.dest_key, BytesIO(source_data))
        
        job.status = OperationStatus.COMPLETED
        
    except Exception as e:
        if 'job' in locals():
            job.status = OperationStatus.FAILED
            job.error_message = str(e)
        await session.commit()
    finally:
        await session.close()
