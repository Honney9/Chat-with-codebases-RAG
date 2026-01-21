from tree_sitter_languages import get_parser

def parse_python_code(code: str):

    parser= get_parser("python")
    tree = parser.parse(bytes(code, "utf-8"))
    root = tree.root_node
    
    functions = []

    for node in root.children:
        if node.type == "functin_definition":
            functions.append(node)
        
        if node.type == "class_definition":
            for child in node.children:
                if child.type == "function_definition":
                    functions.append(child)
    
    return functions