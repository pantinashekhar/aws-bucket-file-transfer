// Wait for DOM to fully load
document.addEventListener('DOMContentLoaded', function() {
    // Check if form exists
    const form = document.getElementById('transferForm');
    if (!form) {
        console.error('Form #transferForm not found!');
        return;
    }
    
    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const sourceBucket = document.getElementById('sourceBucket');
        const sourceKey = document.getElementById('sourceKey');
        const destBucket = document.getElementById('destBucket');
        const destKey = document.getElementById('destKey');
        
        if (!sourceBucket || !sourceKey || !destBucket || !destKey) {
            showStatus({error: 'Form inputs missing'}, 'failed');
            return;
        }
        
        const params = new URLSearchParams({
            source_bucket: sourceBucket.value,
            source_key: sourceKey.value,
            dest_bucket: destBucket.value,
            dest_key: destKey.value
        });
        
        try {
            const response = await fetch(`/api/transfers?${params}`, { 
                method: 'POST',
                headers: { 'Accept': 'application/json' }
            });
            
            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`HTTP ${response.status}: ${errorText}`);
            }
            
            const result = await response.json();
            console.log('✅ Transfer result:', result);
            showStatus(result, 'completed');
            loadRecentJobs();
            pollJobStatus(result.job_id);
            
        } catch (error) {
            console.error('❌ Transfer error:', error);
            showStatus({error: error.message}, 'failed');
        }
    });
    
    // Load recent jobs
    loadRecentJobs();
});

function showStatus(data, statusClass = 'pending') {
    const statusDiv = document.getElementById('status');
    if (!statusDiv) return;
    
    statusDiv.innerHTML = `
        <div class="status ${statusClass}">
            ${data.job_id ? `Job ${data.job_id}: ${data.status?.toUpperCase() || 'STARTED'}` : ''}
            ${data.error ? `<br><strong>Error:</strong> ${data.error}` : ''}
            ${data.message || ''}
        </div>
    `;
}

async function loadRecentJobs() {
    try {
        const response = await fetch('/api/transfers/recent');
        const jobs = await response.json();
        
        const jobList = document.getElementById('jobList');
        if (!jobList) return;
        
        jobList.innerHTML = jobs.length ? 
            jobs.map(job => `
                <div class="status ${job.status}">
                    <strong>${job.jobId}</strong> ${job.status.toUpperCase()}<br>
                    ${job.source} → ${job.dest}
                </div>
            `).join('') : 
            '<em>No recent jobs</em>';
            
    } catch (e) {
        console.error('Recent jobs error:', e);
    }
}

async function pollJobStatus(jobId) {
    const interval = setInterval(async () => {
        try {
            const response = await fetch(`/api/transfers/${jobId}`);
            const job = await response.json();
            
            showStatus(job, job.status);
            loadRecentJobs();
            
            if (job.status === 'completed' || job.status === 'failed') {
                clearInterval(interval);
            }
        } catch (e) {
            console.error('Poll error:', e);
        }
    }, 2000);
}

