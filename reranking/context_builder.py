def build_context(documents, max_chunks: int = 4, max_chars_per_chunk: int = 1500):
    """
    Builds a token-safe context string for LLM input.
    """

    context_blocks = []

    for doc in documents[:max_chunks]:
        metadata = doc.metadata

        code = doc.page_content
        if len(code) > max_chars_per_chunk:
            code = code[:max_chars_per_chunk] + "\n... [truncated]"

        block = f"""
            File: {metadata.get('file_path')}
            Lines: {metadata.get('start_line')} - {metadata.get('end_line')}

            {code}
            """.strip()

        context_blocks.append(block)

    return "\n\n---\n\n".join(context_blocks)
