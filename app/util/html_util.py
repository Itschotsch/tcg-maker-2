import re

def clean_html_text(text: str | None) -> str | None:
    print("CLEANING: ", text)
    if text is None:
        return None

    # Remove URLs like (http://someurl.com/)
    cleaned_text = re.sub(r"\s*\(https?:\/\/[^)]+\)\s*", "", text)

    # Replace self-closing tags like <ignis/> or <ignis> with <ignis></ignis>
    # This handles both <tag/> and <tag> (if it's meant to be an empty tag)
    # The regex captures the tag name and checks for an optional '/'
    # It specifically targets the known tags: ignis, terra, aqua, aeris, magica, unshaped, opt
    cleaned_text = re.sub(
        r"<(ignis|terra|aqua|aeris|magica|unshaped\d*|opt)(/?)>", 
        r"<\1></\1>", 
        cleaned_text
    )
    print(f"Cleaned text: {cleaned_text}")

    return cleaned_text
