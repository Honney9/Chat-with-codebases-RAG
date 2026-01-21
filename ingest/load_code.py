import os
from langchain_core.documents import Document

SUPPORTED_CODE_EXTENSIONS = [
    ".py", ".js", ".jsx", ".ts", ".tsx",
    ".java", ".go", ".html", ".css", ".json"
]

def load_code_files(repo_path: str):
    documents = []

    for root, _, files in os.walk(repo_path):
        for file in files:
            if not any(file.endswith(ext) for ext in SUPPORTED_CODE_EXTENSIONS):
                continue

            file_path = os.path.join(root, file)

            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

                documents.append(
                    Document(
                        page_content=content,
                        metadata={
                            "type": "code",
                            "file_path": file_path,
                            "file_name": file,
                            "extension": os.path.splitext(file)[1],
                        },
                    )
                )

                if file.endswith(".jsx"):
                    print("✅ JSX loaded:", file_path)

            except Exception as e:
                print("❌ Failed:", file_path, e)

    print(f"📦 Total documents loaded: {len(documents)}")
    return documents
