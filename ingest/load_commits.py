from git import Repo
from langchain_core.documents import Document


def load_git_commits(repo_path: str, max_commits: int = 100):
    documents = []

    try:
        repo = Repo(repo_path)
        commits = list(repo.iter_commits())[:max_commits]

        for commit in commits:
            documents.append(
                Document(
                    page_content=commit.message,
                    metadata={
                        "type": "git_commit",
                        "commit_hash": commit.hexsha,
                        "author": commit.author.name,
                        "date": str(commit.committed_datetime),
                    },
                )
            )

    except Exception:
        # Repo might not be a git repo
        pass

    return documents
