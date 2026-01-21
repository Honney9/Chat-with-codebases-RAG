from git import Repo

def get_repo_commit_hash(repo_path: str) -> str:
    repo = Repo(repo_path)
    return repo.head.commit.hexsha
