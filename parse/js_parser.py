from tree_sitter import Parser
from tree_sitter_languages import get_language

JS_LANGUAGE = get_language("javascript")
TS_LANGUAGE = get_language("typescript")
TSX_LANGUAGE = get_language("tsx")


def parse_js_code(code: str, is_ts=False, is_tsx=False):
    parser = Parser()

    if is_tsx:
        parser.set_language(TSX_LANGUAGE)
    elif is_ts:
        parser.set_language(TS_LANGUAGE)
    else:
        parser.set_language(JS_LANGUAGE)

    return parser.parse(code.encode("utf8"))
