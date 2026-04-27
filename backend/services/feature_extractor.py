import ast

def extract_features(code: str):
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None

    num_loops = sum(isinstance(node, (ast.For, ast.While)) for node in ast.walk(tree))
    num_conditions = sum(isinstance(node, ast.If) for node in ast.walk(tree))
    num_functions = sum(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))

    return {
        "num_lines": len(code.split("\n")),
        "num_chars": len(code),
        "num_loops": num_loops,
        "num_conditions": num_conditions,
        "num_functions": num_functions,
        "indentation_issues": 0  # handled via pylint instead
    }