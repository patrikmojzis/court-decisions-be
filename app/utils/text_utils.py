import re


def remove_markdown(text):
    # Handle bold: **bold** or __bold__
    bold_pattern = re.compile(
        r'(?<!\w)(\*\*|__)(?=\S)(.+?)(?<=\S)\1(?!\w)',
        flags=re.DOTALL
    )
    text = bold_pattern.sub(r'\2', text)

    # Handle italic: *italic* or _italic_
    italic_pattern = re.compile(
        r'(?<!\w)(\*|_)(?=\S)(.+?)(?<=\S)\1(?!\w)',
        flags=re.DOTALL
    )
    text = italic_pattern.sub(r'\2', text)

    return text


def count_words(text: str):
   # Split the text into words and count them
   words = text.split()
   return len(words)