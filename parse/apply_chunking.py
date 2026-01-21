from langchain_core.documents import Document
from parse.chunker import chunk_python_code
from parse.js_chunker import chunk_js_code

def apply_code_chunking(documents):
    all_chunks = []

    for doc in documents:
        file_path = doc.metadata.get("file_path", "")
        lines = doc.page_content.splitlines()

        # -------------------------
        # Python
        # -------------------------
        if file_path.endswith(".py"):
            py_chunks = chunk_python_code(doc)

            # 🔑 fallback if no functions
            if py_chunks:
                all_chunks.extend(py_chunks)
            else:
                all_chunks.append(
                    Document(
                        page_content=doc.page_content,
                        metadata={
                            **doc.metadata,
                            "type": "file",
                            "start_line": 1,
                            "end_line": len(lines),
                        }
                    )
                )

        # -------------------------
        # JS / TS
        # -------------------------
        elif file_path.endswith((".js", ".jsx", ".ts", ".tsx")):
            js_chunks = chunk_js_code(doc)

            if js_chunks:
                all_chunks.extend(js_chunks)
            else:
                all_chunks.append(
                    Document(
                        page_content=doc.page_content,
                        metadata={
                            **doc.metadata,
                            "type": "file",
                            "start_line": 1,
                            "end_line": len(lines),
                        }
                    )
                )

        # -------------------------
        # Other files (md, json, yml, etc.)
        # -------------------------
        else:
            all_chunks.append(
                Document(
                    page_content=doc.page_content,
                    metadata={
                        **doc.metadata,
                        "type": "file",
                        "start_line": 1,
                        "end_line": len(lines),
                    }
                )
            )

    return all_chunks
