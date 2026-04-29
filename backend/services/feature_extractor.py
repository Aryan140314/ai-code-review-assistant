import ast


def extract_features(code: str) -> dict | None:
    """
    Extracts numerical features from Python code using AST.
    Returns None if code has a syntax error.
    """
    lines = code.split("\n")
    non_empty = [l for l in lines if l.strip()]
    num_lines = len(lines)

    # Parse the code into an AST so we can count meaningful syntax features.
    try:
        tree = ast.parse(code)
    except SyntaxError:
        # If parsing fails, return a fallback feature set.
        return {
            "num_lines": num_lines,
            "num_chars": len(code),
            "num_loops": 0,
            "num_conditions": 0,
            "num_functions": 0,
            "num_classes": 0,
            "avg_line_length": round(len(code) / num_lines, 2) if num_lines else 0,
            "nesting_depth": 0,
            "num_try_except": 0,
            "num_returns": 0,
            "code_density": 0.0,
        }

    num_loops      = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While)))
    num_conditions = sum(1 for n in ast.walk(tree) if isinstance(n, ast.If))
    num_functions  = sum(1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
    num_classes    = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    num_try_except = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Try))
    num_returns    = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Return))

    # A rough estimate of nesting depth by counting blocks in the AST
    nesting_depth  = sum(
        1 for n in ast.walk(tree)
        if isinstance(n, (ast.For, ast.While, ast.If, ast.With, ast.FunctionDef, ast.ClassDef))
    )

    avg_line_length = round(len(code) / num_lines, 2) if num_lines else 0
    code_density    = round(len(non_empty) / num_lines, 2) if num_lines else 0

    return {
        "num_lines":       num_lines,
        "num_chars":       len(code),
        "num_loops":       num_loops,
        "num_conditions":  num_conditions,
        "num_functions":   num_functions,
        "num_classes":     num_classes,
        "avg_line_length": avg_line_length,
        "nesting_depth":   nesting_depth,
        "num_try_except":  num_try_except,
        "num_returns":     num_returns,
        "code_density":    code_density,
    }