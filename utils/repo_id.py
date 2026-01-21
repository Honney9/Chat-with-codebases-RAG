import hashlib

def get_repo_id(repo_path: str) -> str:
    return hashlib.sha1(repo_path.encode()).hexdigest()
