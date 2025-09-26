"""
FastAPI backend that:
- Receives requests from frontend
- Fetches file list from ANY GitHub repo using GitHub API
- Returns file info to frontend  
- Provides a proxy endpoint to download files from GitHub
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import requests
import io
import zipfile
import re

app = FastAPI()

# Allow frontend (any origin) to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For learning, allow all. Restrict in production!
    allow_methods=["*"],
    allow_headers=["*"],
)

def parse_github_repo_url(url: str):
    """
    Extracts username and repo name from a GitHub repo URL.
    Example: https://github.com/user/repo -> ("user", "repo")
    """
    match = re.match(r"https://github.com/([^/]+)/([^/]+)", url)
    if not match:
        raise HTTPException(status_code=400, detail="Invalid GitHub repo URL")
    return match.group(1), match.group(2)

# --- 1. Endpoint: Get list of files in repo ---
@app.get("/api/files")
def get_files(repo_url: str = Query(..., description="Full GitHub repo URL")):
    """
    Fetches file list from ANY GitHub repo using GitHub API.
    Returns: JSON list of files (name + download_url)
    """
    user, repo = parse_github_repo_url(repo_url)
    github_api_url = f"https://api.github.com/repos/{user}/{repo}/contents/"
    resp = requests.get(github_api_url)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="GitHub API error")
    files = resp.json()
    # Only keep files (not folders), and extract name + download_url
    file_list = [
        {"name": f["name"], "download_url": f["download_url"]}
        for f in files if f.get("type") == "file"
    ]
    return {"files": file_list}

# --- 2. Endpoint: Download a file by URL ---
@app.get("/api/download")
def download_file(url: str):
    """
    Downloads the file from GitHub and sends it to the browser as an attachment.
    """
    if not url.startswith("https://raw.githubusercontent.com/"):
        raise HTTPException(status_code=400, detail="Invalid download URL")
    resp = requests.get(url, stream=True)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="File not found")
    filename = url.split("/")[-1]
    return StreamingResponse(
        resp.iter_content(chunk_size=8192),
        media_type=resp.headers.get("content-type", "application/octet-stream"),
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# --- 3. Endpoint: Download all files as zip ---
@app.get("/api/download_all")
def download_all_files(repo_url: str = Query(..., description="Full GitHub repo URL")):
    """
    Downloads all files from ANY GitHub repo, zips them, and sends as a single zip file.
    """
    user, repo = parse_github_repo_url(repo_url)
    github_api_url = f"https://api.github.com/repos/{user}/{repo}/contents/"
    resp = requests.get(github_api_url)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="GitHub API error")
    files = resp.json()
    file_list = [
        {"name": f["name"], "download_url": f["download_url"]}
        for f in files if f.get("type") == "file"
    ]

    # Create a zip in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zip_file:
        for file in file_list:
            file_resp = requests.get(file["download_url"])
            if file_resp.status_code == 200:
                zip_file.writestr(file["name"], file_resp.content)
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={repo}_all_files.zip"}
    )

# --- 4. Root endpoint for testing ---
@app.get("/")
def home():
    return {"message": "FastAPI backend is running! Paste your GitHub repo link to fetch files."}