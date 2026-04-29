def generate_suggestions(issues: list, features: dict) -> list:
    suggestions = []

    if features.get("num_functions", 0) == 0 and features.get("num_lines", 0) > 10:
        suggestions.append("Break your code into functions for better readability and reuse.")

    if features.get("avg_line_length", 0) > 80:
        suggestions.append("Keep lines under 80 characters — long lines hurt readability.")

    if features.get("nesting_depth", 0) > 5:
        suggestions.append("Reduce nesting depth by extracting inner blocks into separate functions.")

    if features.get("num_loops", 0) > 4:
        suggestions.append("High loop count — consider list comprehensions or built-in functions like map/filter.")

    if features.get("num_try_except", 0) == 0 and features.get("num_lines", 0) > 30:
        suggestions.append("Add error handling (try/except) for production-safe code.")

    if features.get("num_classes", 0) == 0 and features.get("num_lines", 0) > 100:
        suggestions.append("Large file with no classes — consider organizing into classes or modules.")

    if features.get("code_density", 1) < 0.5:
        suggestions.append("Too many blank lines — clean up unnecessary whitespace.")

    # Issue-based suggestions
    seen = set()
    for issue in issues:
        issue_lower = issue.lower()
        if "unused" in issue_lower and "import" in issue_lower and "remove-imports" not in seen:
            suggestions.append("Remove unused imports to keep the code clean.")
            seen.add("remove-imports")
        elif ("naming" in issue_lower or "snake_case" in issue_lower) and "naming" not in seen:
            suggestions.append("Follow PEP8 naming: snake_case for variables/functions, PascalCase for classes.")
            seen.add("naming")
        elif "docstring" in issue_lower and "docstring" not in seen:
            suggestions.append("Add docstrings to all public functions and classes.")
            seen.add("docstring")
        elif "too-many" in issue_lower and "too-many" not in seen:
            suggestions.append("Function is too large — split it into smaller focused functions.")
            seen.add("too-many")

    return list(dict.fromkeys(suggestions))[:6]  # deduplicate, cap at 6