#!/usr/bin/env python3

"""
Markdown processing functions. This module should subusme the functions from the
old html_to_markdown_canlii.py script.
"""

from typing import Tuple, List

def import_markdown_file(file_path: str) -> str:
    """
    Reads the contents of a markdown file from a given path.

    Args:
        file_path (str): The path to the markdown file.

    Returns:
        str: The content of the file as a string, or an error message if an error occurs.
    """

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except FileNotFoundError:
        return "File not found."


def split_text_at_delimiter(text: str, delimiter: str = "\n__\n") -> Tuple[str, str]:
    """
    Splits the text at the first occurrence of the specified delimiter.

    Args:
        text (str): The text to be split.
        delimiter (str): The delimiter at which to split the text. Default is "\n__\n".

    Returns:
        Tuple[str, str]: A tuple of two strings, (before_delimiter, after_delimiter).
    """

    delimiter_index = text.find(delimiter)
    if delimiter_index == -1:
        return text, ""

    before_delimiter = text[:delimiter_index]
    after_delimiter = text[delimiter_index + len(delimiter) :]

    return before_delimiter, after_delimiter


def process_markdown(text: str) -> Tuple[List[str], str]:
    """
    Processes a markdown text string and extracts its metadata lines and main content.

    Args:
        text (str): The markdown text to be processed.

    Returns:
        Tuple[List[str], str]: A tuple containing metadata_lines (a list of metadata lines)
        and main_content (the content of the markdown text as a string).

        These steps are specific to SKCA decisions from 2015 to present (2023).
    """

    # Split the markdown text at the first occurrence of "\n__\n"
    metadata, main_content = split_text_at_delimiter(text, "\n__\n")
    metadata = metadata.split("[Home]")[1]

    

    metadata_lines = [line for line in metadata.splitlines() if line.strip()]

    # Corrects for some irregularities in the metadata
    # Decide whether to keep these functions here or move them to the refine_markdown function
    # Another option is to pull in all the refine_markdown functions from the other scripts here
    # Remove junk lines, including "*"s and whitespace

    metadata_lines = [
        line
        for line in metadata_lines
        if "Expanded Collapsed" not in line and "[PDF]" not in line
    ]

    # If both "File number:" and "Other citations:" are present, move "Other citations:" to the next line
    # Corrects for an error in some SKCA decisions
    if "File number:" in metadata_lines and "Other citations:" in metadata_lines:
        file_number_index = metadata_lines.index("File number:")
        other_citations_index = metadata_lines.index("Other citations:")
        metadata_lines.insert(other_citations_index + 1, metadata_lines.pop(file_number_index))

    if "File number:" in metadata_lines and "Other citation:" in metadata_lines:
        file_number_index = metadata_lines.index("File number:")
        other_citations_index = metadata_lines.index("Other citation:")
        metadata_lines.insert(other_citations_index + 1, metadata_lines.pop(file_number_index))

    # Remove asterisks wherever they appear
    metadata_lines = [line.replace("*", "") for line in metadata_lines]

    # Remove whitespace at the beginning and end of each line
    metadata_lines = [line.strip() for line in metadata_lines]

    # Remove lines that start with the string "![]"
    metadata_lines = [line for line in metadata_lines if not line.startswith("![]")]

    return metadata_lines, main_content
