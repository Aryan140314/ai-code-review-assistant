import ast
import re


def extract_features(code: str) -> dict:
    lines = code.split("\n")
    non_empty = [l for l in lines if l.strip()]
    num_lines = len(lines)

    # --- Basic counts ---
    num_chars = len(code)
    avg_line_length = round(num_chars / num_lines, 2) if num_lines else 0
    code_density = round(len(non_empty) / num_lines, 2) if num_lines else 0

    # --- String-based signals ---
    num_comments = sum(1 for l in lines if l.strip().startswith("#"))
    has_docstring = int('"""' in code or "'''" in code)
    num_magic_numbers = len(re.findall(r'\b(?<!\w)\d{2,}\b', code))  # numbers > 9 not in strings
    num_print_statements = code.count("print(")
    num_bare_except = len(re.findall(r'except\s*:', code))

    # --- AST-based ---
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return {
            "num_lines": num_lines,
            "num_chars": num_chars,
            "num_loops": 0,
            "num_conditions": 0,
            "num_functions": 0,
            "num_classes": 0,
            "avg_line_length": avg_line_length,
            "max_nesting_depth": 0,
            "num_try_except": 0,
            "num_returns": 0,
            "code_density": code_density,
            "num_comments": num_comments,
            "has_docstring": 0,
            "num_magic_numbers": num_magic_numbers,
            "num_print_statements": num_print_statements,
            "num_bare_except": num_bare_except,
            "avg_function_length": 0,
            "num_global_vars": 0,
            "cyclomatic_complexity": 1,
        }

    num_loops      = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While)))
    num_conditions = sum(1 for n in ast.walk(tree) if isinstance(n, ast.If))
    num_functions  = sum(1 for n in ast.walk(tree) if isinstance(n, ast.FunctionDef))
    num_classes    = sum(1 for n in ast.walk(tree) if isinstance(n, ast.ClassDef))
    num_try_except = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Try))
    num_returns    = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Return))
    num_global_vars = sum(1 for n in ast.walk(tree) if isinstance(n, ast.Global))

    # Max nesting depth (real depth tracking)
    max_nesting_depth = _get_max_depth(tree)

    # Average function length in lines
    func_lengths = []
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            if hasattr(node, 'end_lineno') and hasattr(node, 'lineno'):
                func_lengths.append(node.end_lineno - node.lineno)
    avg_function_length = round(sum(func_lengths) / len(func_lengths), 2) if func_lengths else 0

    # Cyclomatic complexity estimate: 1 + branches
    cyclomatic_complexity = 1 + num_conditions + num_loops + num_try_except

    return {
        "num_lines":            num_lines,
        "num_chars":            num_chars,
        "num_loops":            num_loops,
        "num_conditions":       num_conditions,
        "num_functions":        num_functions,
        "num_classes":          num_classes,
        "avg_line_length":      avg_line_length,
        "max_nesting_depth":    max_nesting_depth,
        "num_try_except":       num_try_except,
        "num_returns":          num_returns,
        "code_density":         code_density,
        "num_comments":         num_comments,
        "has_docstring":        has_docstring,
        "num_magic_numbers":    num_magic_numbers,
        "num_print_statements": num_print_statements,
        "num_bare_except":      num_bare_except,
        "avg_function_length":  avg_function_length,
        "num_global_vars":      num_global_vars,
        "cyclomatic_complexity": cyclomatic_complexity,
    }


def _get_max_depth(tree) -> int:
    """Recursively find the real maximum nesting depth."""
    def depth(node, current=0):
        if isinstance(node, (ast.For, ast.While, ast.If, ast.With,
                              ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            current += 1
        max_d = current
        for child in ast.iter_child_nodes(node):
            max_d = max(max_d, depth(child, current))
        return max_d
    return depth(tree)