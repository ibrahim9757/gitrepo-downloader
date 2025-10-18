"""
FastAPI backend that:
- Receives requests from frontend
- Fetches file list from ANY GitHub repo using GitHub API
- Returns file info to frontend  
- Provides a proxy endpoint to download files from GitHub
"""

import os
import io
import zipfile
import requests
from typing import List, Dict

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from urllib.parse import urlparse
from datetime import datetime

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
    Robustly extract owner and repo from various GitHub URL formats:
    - https://github.com/owner/repo
    - https://github.com/owner/repo.git
    - https://github.com/owner/repo/tree/branch/...
    - git@github.com:owner/repo.git
    - owner/repo
    """
    if not url or not isinstance(url, str):
        raise HTTPException(status_code=400, detail="Invalid GitHub repo URL")

    url = url.strip()

    # Handle SSH-style URLs: git@github.com:owner/repo.git
    if url.startswith("git@"):
        try:
            user_repo = url.split(":", 1)[1]
        except IndexError:
            raise HTTPException(status_code=400, detail="Invalid GitHub repo URL")
    else:
        parsed = urlparse(url)
        # If it's a full GitHub URL, take the path; otherwise assume it's owner/repo
        if parsed.netloc and "github.com" in parsed.netloc.lower():
            user_repo = parsed.path.lstrip("/")
        else:
            user_repo = url  # allow "owner/repo" shorthand

    # Keep only the owner and repo (ignore extra segments like tree/branch)
    parts = user_repo.split("/")
    if len(parts) < 2 or not parts[0] or not parts[1]:
        raise HTTPException(status_code=400, detail="Invalid GitHub repo URL")

    owner = parts[0]
    repo = parts[1]

    # Strip .git suffix if present
    if repo.endswith(".git"):
        repo = repo[:-4]

    return owner, repo

# Create a requests session with sensible headers and optional token
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
session = requests.Session()
session.headers.update({
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "gitrepo-downloader"
})
if GITHUB_TOKEN:
    session.headers.update({"Authorization": f"token {GITHUB_TOKEN}"})

def _fetch_contents_recursive(owner: str, repo: str, path: str = "") -> List[Dict]:
    """
    Recursively fetch files from GitHub API contents endpoint.
    Returns list of dicts: { "name": <basename>, "path": <relative/path/in/repo>, "download_url": <raw url> }
    """
    base = f"https://api.github.com/repos/{owner}/{repo}/contents"
    url = base + (f"/{path}" if path else "")
    resp = session.get(url)
    if resp.status_code == 404:
        raise HTTPException(status_code=404, detail="Repository or path not found")
    if resp.status_code == 403:
        # Try to surface rate-limit info if available
        reset = resp.headers.get("X-RateLimit-Reset")
        if reset:
            reset_ts = int(reset)
            reset_time = datetime.utcfromtimestamp(reset_ts).strftime("%Y-%m-%d %H:%M:%S UTC")
            detail = f"GitHub API rate limit exceeded. Limit resets at {reset_time}. Set GITHUB_TOKEN to increase limits."
        else:
            detail = "GitHub API returned 403 Forbidden. Possibly rate-limited or repository is private. Set GITHUB_TOKEN env var if needed."
        raise HTTPException(status_code=403, detail=detail)
    if resp.status_code != 200:
        raise HTTPException(status_code=resp.status_code, detail="GitHub API error")
    items = resp.json()
    files: List[Dict] = []
    # items can be a single file object when path points to a file
    if isinstance(items, dict) and items.get("type") == "file":
        files.append({
            "name": items["name"],
            "path": items.get("path", items["name"]),
            "download_url": items.get("download_url")
        })
        return files

    for item in items:
        itype = item.get("type")
        if itype == "file":
            files.append({
                "name": item["name"],
                "path": item.get("path", item["name"]),
                "download_url": item.get("download_url")
            })
        elif itype == "dir":
            subpath = item.get("path")
            files.extend(_fetch_contents_recursive(owner, repo, subpath))
        # ignore other types (symlink, submodule) for now
    return files

# --- 1. Endpoint: Get list of files in repo ---
@app.get("/api/files")
def get_files(repo_url: str = Query(..., description="Full GitHub repo URL")):
    """
    Fetches file list from ANY GitHub repo using GitHub API.
    Returns: JSON list of files (name + path + download_url)
    """
    user, repo = parse_github_repo_url(repo_url)
    file_list = _fetch_contents_recursive(user, repo, path="")
    return {"files": file_list}

# --- 2. Endpoint: Download a file by URL ---
@app.get("/api/download")
def download_file(url: str):
    """
    Downloads the file from GitHub and sends it to the browser as an attachment.
    """
    if not url.startswith("https://raw.githubusercontent.com/"):
        raise HTTPException(status_code=400, detail="Invalid download URL")
    resp = session.get(url, stream=True)
    if resp.status_code == 403:
        raise HTTPException(status_code=403, detail="Forbidden when fetching file. Provide GITHUB_TOKEN if needed.")
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
    Downloads all files from ANY GitHub repo, zips them preserving folder structure,
    and sends as a single zip file.
    """
    user, repo = parse_github_repo_url(repo_url)
    file_list = _fetch_contents_recursive(user, repo, path="")

    if not file_list:
        raise HTTPException(status_code=404, detail="No files found in repository")

    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for file in file_list:
            dl_url = file.get("download_url")
            if not dl_url:
                continue
            file_resp = session.get(dl_url)
            if file_resp.status_code == 403:
                raise HTTPException(status_code=403, detail="Forbidden when fetching file. Provide GITHUB_TOKEN if needed.")
            if file_resp.status_code != 200:
                # skip missing files but continue zipping others
                continue
            arcname = file.get("path", file.get("name"))
            zip_file.writestr(arcname, file_resp.content)
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={repo}_all_files.zip"}
    )

# --- 4. Root endpoint for testing ---
@app.get("/")
def home():
    return {"message": "Backend is running. Use /api/files and /api/download_all endpoints."}
