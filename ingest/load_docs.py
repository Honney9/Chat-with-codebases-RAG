import os
from langchain_core.documents import Document

SUPPORTED_DOC_EXTENSIONS = [".md", ".txt"]

def load_doc_files(repo_path: str):
    documents = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            if any(file.lower().endswith(ext) for ext in SUPPORTED_DOC_EXTENSIONS):
                file_path = os.path.join(root, file)

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        content = f.read()

                    documents.append(
                        Document(
                            page_content=content,
                            metadata={
                                "type": "documentation",
                                "file_path": file_path,
                                "file_name": file,
                            }
                        )
                    )
                except Exception:
                    continue
    
    return documents