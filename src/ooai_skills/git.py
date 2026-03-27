from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import requests

def is_git_available() -> bool:
    return shutil.which('git') is not None

def clone_repo(repo: str, ref: str, dest: Path) -> str:
    if is_git_available():
        return _clone_with_git(repo, ref, dest)
    return _download_zip(repo, ref, dest)

def _clone_with_git(repo: str, ref: str, dest: Path) -> str:
    url = f'https://github.com/{repo}.git'
    if dest.exists() and (dest / '.git').exists():
        subprocess.run(['git','-C',str(dest),'fetch','--depth','1','origin',ref], check=True)
        subprocess.run(['git','-C',str(dest),'checkout','--force','FETCH_HEAD'], check=True)
    else:
        dest.parent.mkdir(parents=True, exist_ok=True)
        subprocess.run(['git','clone','--depth','1','--branch',ref,url,str(dest)], check=True)
    res = subprocess.run(['git','-C',str(dest),'rev-parse','HEAD'], check=True, capture_output=True, text=True)
    return res.stdout.strip()

def _download_zip(repo: str, ref: str, dest: Path) -> str:
    url = f'https://github.com/{repo}/archive/refs/heads/{ref}.zip'
    dest.parent.mkdir(parents=True, exist_ok=True)
    r = requests.get(url, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f'Failed to download {repo}@{ref}: {r.status_code}')
    zip_path = dest.with_suffix('.zip')
    zip_path.write_bytes(r.content)
    import zipfile
    if dest.exists():
        shutil.rmtree(dest)
    with zipfile.ZipFile(zip_path,'r') as zf:
        zf.extractall(dest.parent)
    extracted_dirs = [p for p in dest.parent.iterdir() if p.is_dir() and p.name.startswith(repo.split('/',1)[1]+'-')]
    if not extracted_dirs:
        raise RuntimeError('Archive extracted unexpectedly')
    extracted_dirs[0].rename(dest)
    zip_path.unlink(missing_ok=True)
    return ref
