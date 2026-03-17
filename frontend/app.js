const API_BASE_URL = "http://127.0.0.1:8000";

function showLoading(show) {
    document.getElementById('loading').classList.toggle('hidden', !show);
    document.getElementById('result-section').classList.add('hidden');
}

function displayResults(data) {
    document.getElementById('res_post').innerText = data.post_score;
    document.getElementById('res_comment').innerText = data.comment_score;
    document.getElementById('res_icp').innerText = data.ICP_score;
    document.getElementById('res_advice').innerText = data.advice;
    
    document.getElementById('loading').classList.add('hidden');
    document.getElementById('result-section').classList.remove('hidden');
}

// Mode 1: URL
async function analyzeUrl() {
    const url = document.getElementById('post_url').value;
    const icp = document.getElementById('icp').value;

    if (!url) return alert("Please enter a LinkedIn URL.");

    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/api/analyze/url`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ post_url: url, reference_icp: icp })
        });
        
        if (!response.ok) throw new Error(await response.text());
        const data = await response.json();
        displayResults(data);
    } catch (error) {
        alert("Error: " + error.message);
        showLoading(false);
    }
}

// Mode 2: CSV File
async function analyzeFiles() {
    const postFile = document.getElementById('post_file').files[0];
    const commentsFile = document.getElementById('comments_file').files[0];
    const icp = document.getElementById('icp').value;

    if (!postFile || !commentsFile) return alert("Please select both Post and Comments CSV files.");

    const formData = new FormData();
    formData.append("reference_icp", icp);
    formData.append("post_file", postFile);
    formData.append("comments_file", commentsFile);

    showLoading(true);
    try {
        const response = await fetch(`${API_BASE_URL}/api/analyze/files`, {
            method: 'POST',
            body: formData // Fetch automatically sets head: multipart/form-data
        });
        
        if (!response.ok) throw new Error(await response.text());
        const data = await response.json();
        displayResults(data);
    } catch (error) {
        alert("Error: " + error.message);
        showLoading(false);
    }
}