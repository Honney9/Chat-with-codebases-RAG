import hashlib

def make_chunk_id(
    repo_id: str,
    file_path: str,
    start_line: int,
    end_line: int,
    commit_hash: str
) -> str:
    raw = f"{repo_id}:{file_path}:{start_line}:{end_line}:{commit_hash}"
    return hashlib.sha256(raw.encode()).hexdigest()