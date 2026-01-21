from langchain_core.documents import Document
from parse.parser import parse_python_code
from indexing.path_utils import normalize_path



def chunk_python_code(document: Document):
    code = document.page_content
    file_path = normalize_path(document.metadata.get("file_path"))
    lines = code.splitlines()

    chunks = []
    functions = parse_python_code(code)

    for fn in functions:
        start_line = fn.start_point[0] + 1
        end_line = fn.end_point[0] + 1

        fn_code = "\n".join(lines[start_line - 1:end_line])

        chunks.append(
            Document(
                page_content=fn_code,
                metadata={
                    "type": "function",
                    "file_path": file_path,
                    "function_name": fn.child_by_field_name("name").text.decode(),
                    "start_line": start_line,
                    "end_line": end_line,
                }
            )
        )

    # 🔑 FALLBACK: whole file
    if not chunks:
        chunks.append(
            Document(
                page_content=code,
                metadata={
                    "type": "file",
                    "file_path": file_path,
                    "start_line": 1,
                    "end_line": len(lines),
                }
            )
        )

    return chunks
