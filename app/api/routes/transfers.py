from fastapi import APIRouter, Depends, HTTPException, Query , BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import Session
from app.db.session import get_session 
from uuid import uuid4
from app.db.session import get_session, AsyncSessionLocal
from app.db.models import TransferJob, OperationStatus
from app.storage.deps import get_storage_client
from app.storage.base import StorageClient
from fastapi import BackgroundTasks
from io import BytesIO
import logging

logging.getLogger().setLevel(logging.INFO)
logger = logging.getLogger(__name__)
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
    job = TransferJob(  # Remove job_id=
        source_bucket=source_bucket,
        source_key=source_key,
        dest_bucket=dest_bucket,
        dest_key=dest_key,
        status=OperationStatus.PENDING  # ✅ Enum
    )
    session.add(job)
    await session.commit()
    await session.refresh(job)  # ✅ Gets job_id
    
    background_tasks.add_task(perform_transfer, job.id, storage)
    
    return {
        "job_id": job.job_id,  # ✅ Now populated
        "status": job.status.value,  # If enum needs .value
        "message": "Transfer queued"
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
    "jobId": job.id,  # Not job.job_id
    "status": job.status,
    "source": f"{job.source_bucket}/{job.source_key}",
    "dest": f"{job.dest_bucket}/{job.dest_key}",
    "created_at": job.created_at.isoformat() if job.created_at else None
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
    # ✅ Correct - import and use get_session dependency pattern
    # Add this import
    async with get_session() as session:  # Or await get_db() if it's a generator  # Reuse get_session dep
        job = await session.get(TransferJob, job_id)
        if not job: return
        logger.info(f"🔥 BACKGROUND START {job.job_id}")
        job.status = OperationStatus.IN_PROGRESS
        await session.commit()
        try:
            data = await storage.download_file(job.source_bucket, job.source_key)
            logger.info(f"📥 {len(data)} bytes")
            await storage.upload_file(job.dest_bucket, job.dest_key, data)
            logger.info("📤 UPLOADED")
            job.status = OperationStatus.COMPLETED
        except Exception as e:
            job.status = OperationStatus.FAILED
            job.error_message = str(e)
            logger.error(f"💥 {e}")
        await session.commit()


