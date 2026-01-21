def filter_by_file_type(documents, file_extension=None):
    if not file_extension:
        return documents

    return [
        doc for doc in documents
        if doc.metadata.get("file_path", "").endswith(file_extension)
    ]

def filter_by_function_name(documents, function_name = None):
    if not function_name:
        return documents
    
    return [
        doc for doc in documents
        if function_name.lower() in doc.metadata.get("function_name", "").lower()
    ]