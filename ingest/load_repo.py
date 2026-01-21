import os
import shutil
import tempfile
from git import Repo
from langchain_core.documents import Document

SUPPORTED_EXTENSIONS = (
    ".py", ".js", ".ts", ".tsx", ".jsx",
    ".java", ".go",
    ".md", ".txt", ".yaml", ".yml", ".json"
)

EXCLUDE_DIRS = {
    ".git",
    "node_modules",
    "venv",
    "__pycache__",
    ".next",
    "dist",
    "build"
}

def load_repository(repo_path: str):
    print("[DEBUG] load_repository called with:", repo_path, flush=True)

    documents = []

    if repo_path.startswith("http"):
        temp_dir = tempfile.mkdtemp()
        print("[DEBUG] Cloning repo to:", temp_dir, flush=True)

        try:
            Repo.clone_from(repo_path, temp_dir)
            base_path = temp_dir
        except Exception as e:
            shutil.rmtree(temp_dir)
            raise RuntimeError(f"Failed to clone repo: {e}")
    else:
        if not os.path.exists(repo_path):
            raise ValueError(f"Local path does not exist: {repo_path}")

        base_path = repo_path
        print("[DEBUG] Using local repo:", base_path, flush=True)

    file_count = 0

    for root, dirs, files in os.walk(base_path):
        # 🚨 CRITICAL: skip heavy folders
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        for file in files:
            if file.endswith(SUPPORTED_EXTENSIONS):
                full_path = os.path.join(root, file)

                try:
                    with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                        content = f.read()

                    documents.append(
                        Document(
                            page_content=content,
                            metadata={
                                "type": "file",   # ✅ ADD THIS
                                "file_path": full_path.replace(base_path, ""),
                                "source": "local",
                                "extension": os.path.splitext(file)[1],
                            }
                        )
                    )
                    file_count += 1

                except Exception as e:
                    print("[DEBUG] Failed reading:", full_path, e, flush=True)
                    continue

    print(f"[DEBUG] Total documents loaded: {file_count}", flush=True)

    return documents, base_path
