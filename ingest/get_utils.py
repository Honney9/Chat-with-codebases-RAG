import subprocess

def get_repo_commit_hash(repo_path: str) -> str:
    return subprocess.check_output(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path
    ).decode("utf-8").strip()
