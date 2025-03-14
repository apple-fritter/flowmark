def split_frontmatter(text: str) -> tuple[str, str]:
    """
    Split a text document into frontmatter and content parts.

    Checks if the string starts with YAML frontmatter, delimited by `---`
    lines. If so, returns the frontmatter, including the `---` lines, and the
    rest of the document. If no frontmatter is found, returns an empty string
    and the original text.
    """
    lines = text.splitlines()

    # Skip empty lines at the beginning
    start_idx = 0
    while start_idx < len(lines) and lines[start_idx].strip() == "":
        start_idx += 1

    # If no content or doesn't start with '---', return empty frontmatter
    if start_idx >= len(lines) or lines[start_idx].strip() != "---":
        return "", text

    # Look for the closing '---'
    end_idx = start_idx + 1
    while end_idx < len(lines):
        if lines[end_idx].strip() == "---":
            # Found the closing delimiter - extract frontmatter and content
            frontmatter = "\n".join(lines[start_idx : end_idx + 1]) + "\n"
            content = "\n".join(lines[end_idx + 1 :])
            return frontmatter, content
        end_idx += 1

    # If no closing delimiter found, everything is considered frontmatter
    # and nothing should change
    return text, ""


def has_frontmatter(text: str) -> bool:
    """
    Check if the text starts with YAML frontmatter.
    """
    frontmatter, _ = split_frontmatter(text)
    return frontmatter != ""
