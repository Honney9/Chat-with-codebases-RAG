from langchain_core.documents import Document
from parse.js_parser import parse_js_code

FUNCTION_NODES = {
    "function_declaration",
    "method_definition",
    "arrow_function",
}

def chunk_js_code(document: Document):
    code = document.page_content
    file_path = document.metadata.get("file_path").lower()

    is_ts = file_path.endswith(".ts")
    is_tsx = file_path.endswith((".tsx", ".jsx"))

    tree = parse_js_code(code, is_ts=is_ts, is_tsx=is_tsx)
    root = tree.root_node
    lines = code.splitlines()

    chunks = []
    found_function = False

    def find_body(node):
        """Recursively find a block_statement (function body)"""
        if node.type == "statement_block":
            return node
        for child in node.children:
            result = find_body(child)
            if result:
                return result
        return None

    def walk(node):
        nonlocal found_function

        if node.type in FUNCTION_NODES:
            found_function = True

            start_line = node.start_point[0] + 1

            body = find_body(node)
            if body:
                end_line = body.end_point[0] + 1
            else:
                end_line = node.end_point[0] + 1

            fn_code = "\n".join(lines[start_line - 1:end_line])

            chunks.append(
                Document(
                    page_content=fn_code,
                    metadata={
                        **document.metadata,
                        "type": "function",
                        "start_line": start_line,
                        "end_line": end_line,
                    }
                )
            )

        for child in node.children:
            walk(child)

    walk(root)

    # ✅ Add full-file chunk ONLY if no functions found
    if not found_function:
        chunks.append(
            Document(
                page_content=code,
                metadata={
                    **document.metadata,
                    "type": "file",
                    "start_line": 1,
                    "end_line": len(lines),
                }
            )
        )

    return chunks
