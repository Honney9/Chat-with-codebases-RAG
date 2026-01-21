import hashlib

def get_repo_id(repo_path: str) -> str:
    return hashlib.sha256(repo_path.strip().lower().encode()).hexdigest()
