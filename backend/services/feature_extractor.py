def extract_features(code: str):
    lines = code.split("\n")

    return {
        "num_lines": len(lines),
        "num_chars": len(code),
        "num_loops": code.count("for") + code.count("while"),
        "num_conditions": code.count("if"),
        "num_functions": code.count("def"),
        "indentation_issues": code.count("  ")
    }