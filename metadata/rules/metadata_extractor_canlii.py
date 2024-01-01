"""
Broad function that extracts metadata from a CanLII markdown file and saves it to a JSON file.
Currently designed to work with SKCA decisions from 2015 to present (2023).
"""

#!/usr/bin/env python3

import json
import os
import re
import pandas as pd
from typing import Tuple, List, Dict, Any
from dateutil.parser import parse
import typer

app = typer.Typer()

###
# General purpose functions
###


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


def create_metadata_md(file_path: str) -> str:
    """
    Processes a markdown file and prints its metadata line by line,
    starting from the first line that begins with the "#" character.

    Args:
        file_path (str): The path to the markdown file.

    Returns:
        str: The content of the file as a string, or an error message if an error occurs.

        These steps are specific to SKCA decisions from 2015 to present (2023).

    """

    content = import_markdown_file(file_path)
    if content.startswith("An error occurred") or content == "File not found.":
        typer.echo(content)
        return

    # Split the markdown file at the first occurrence of "\n__\n"
    metadata, main_content = split_text_at_delimiter(content, "\n__\n")
    metadata_lines = [line for line in metadata.splitlines() if line.strip()]

    # Corrects for some irregularities in the metadata
    # Remove junk lines, including "*"s and whitespace

    metadata_lines = [
        line
        for line in metadata_lines
        if "Expanded Collapsed" not in line and "[PDF]" not in line
    ]

    # Remove asterisks wherever they appear
    metadata_lines = [line.replace("*", "") for line in metadata_lines]

    return metadata_lines, main_content


###
# Functions specific to SKCA decisions from 2015 to present (2023)
###


@app.command()
def skca_2015(file_path: str):
    """
    Processes a markdown file and prints its metadata line by line,
    starting from the first line that begins with the "#" character.

    These steps are specific to SKCA decisions from 2015 to present (2023).

    Args:
        file_path (str): The path to the markdown file.

    """

    metadata_lines = create_metadata_md(file_path)[0]

    # Splits the "File number" and "Citation" lines found in recent SKCA decisions
    for index, item in enumerate(metadata_lines):
        if "number:" in item and "Citation:" in item:
            file_number, citation = item.split("Citation:", 1)

            if "File number:" not in file_number:
                file_number = file_number.replace("number:", "File number:")

            metadata_lines[index] = file_number
            metadata_lines.insert(index + 1, f"Citation:{citation}")

    # Remove the last line if it starts with "#"
    # Then remove the next (reduntant) last line containing the decision's author
    if metadata_lines[-1].startswith("#"):
        metadata_lines = metadata_lines[:-1]
        metadata_lines.pop()
    else:
        metadata_lines.pop()

    # Run the mteadata lines through the processing functions
    metadata_dict = process_metadata_lines(metadata_lines)
    output_file_name = save_metadata_to_json(file_path, metadata_dict)

    typer.echo(f"Metadata exported to JSON file: {output_file_name}")
    typer.echo("Metadata Key-Value Pairs:")
    for key, value in metadata_dict.items():
        typer.echo(f"{key}: {value}")


def define_judicial_aggregate(metadata_dict: dict, key: str) -> None:
    """
    Defines a judicial aggregate in the metadata dictionary. Designed to work with skca_2015().

    Args:
        metadata_dict (Dict[str, Any]): The metadata dictionary.
        key (str): The key to be defined as a judicial aggregate.
    """
    split_pattern = "The Honourable "
    if key in metadata_dict:
        value = metadata_dict[key]
        value = value.split(split_pattern)
        value = [item.strip() for item in value]
        value = [item for item in value if item]
        metadata_dict[key] = value
    else:
        metadata_dict[key] = []


def define_parties(metadata_dict: dict) -> None:
    """
    Defines the parties in the metadata dictionary. Designed to work with skca_2015().

    Args:
        metadata_dict (Dict[str, Any]): The metadata dictionary.
    """
    if "between" in metadata_dict:
        # Split the string at the word "and"
        between_value = metadata_dict["between"]
        between_value = between_value.split("And ")

        # Remove "between" from metadata_dict
        metadata_dict.pop("between")

        # Add the split string to metadata_dict
        metadata_dict["between"] = between_value


def identify_case_type(metadata_dict: dict) -> None:
    """
    Examines the "docket" key in the metadata dictionary and identifies the case type. To do so,
    the function checks the first four characters of the docket number. If the first four characters
    are "CACV", the case type is "Civil Appeal". If the first four characters are "CACR", the case
    type is "Criminal Appeal".

    Args:
        metadata_dict (Dict[str, Any]): The metadata dictionary.
    """

    if "docket" in metadata_dict:
        docket_value = metadata_dict["docket"]
        if docket_value.startswith("CACV"):
            metadata_dict["case_type"] = "civil appeal"
        elif docket_value.startswith("CACR"):
            metadata_dict["case_type"] = "criminal appeal"


def extract_dates(text: str) -> List[str]:
    """
    Extracts dates from a string in the format "Month Day, Year" and returns a list of dates in
    YYYY-MM-DD format.

    Args:
        text (str): The string from which to extract dates.

    Returns:
        List[str]: A list of dates in YYYY-MM-DD format.
    """

    month_year_match = re.search(
        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\b",
        text,
    )
    if month_year_match:
        month = month_year_match.group()
    else:
        # If no month is found, return an empty list or handle as needed
        return []

    # Find the year in the string
    year_match = re.search(r"\b\d{4}\b", text)
    if year_match:
        year = year_match.group()
    else:
        # If no year is found, return an empty list or handle as needed
        return []

    # Find all individual days
    days = re.findall(r"\b\d{1,2}\b", text)

    # List to hold the final dates
    dates = []

    for day in days:
        # Parse and format each date
        date_str = f"{month} {day}, {year}"
        date = parse(date_str)
        dates.append(date.strftime("%Y-%m-%d"))

    return dates


def convert_appeal_heard_date(metadata_dict: dict) -> None:
    """
    Converts the "appeal heard" key in the metadata dictionary to a list of dates in YYYY-MM-DD
    format, or saves it as a single-item list containing the original string if formatting fails.
    Designed to work with skca_2015().

    Args:
        metadata_dict (Dict[str, Any]): The metadata dictionary.
    """

    if "appeal heard" in metadata_dict:
        date_str = metadata_dict["appeal heard"]
        try:
            metadata_dict["appeal heard"] = extract_dates(date_str)
        except ValueError:
            metadata_dict["appeal heard"] = [date_str]

    if "appeals heard" in metadata_dict:
        date_str = metadata_dict["appeals heard"]
        try:
            metadata_dict["appeal heard"] = extract_dates(date_str)
        except ValueError:
            metadata_dict["appeal heard"] = [date_str]


def process_metadata_lines(metadata_lines: List[str]) -> Dict[str, Any]:
    """
    Processes metadata lines to extract key-value pairs and specific formats.

    Args:
        metadata_lines (List[str]): The list of metadata lines.

    Returns:
        Dict[str, Any]: A dictionary containing processed metadata.
    """
    metadata_dict = {}
    current_key = None
    current_value = []

    for line in metadata_lines:
        # Handling URL extraction
        if "<<" in line and ">>" in line:
            start, end = line.find("<<") + 2, line.find(">>")
            metadata_dict["url"] = line[start:end].strip()
            line = line[: start - 2] + line[end + 2 :]

        # Handling key-value pairs
        if ":" in line:
            if current_key:
                metadata_dict[current_key.lower()] = " ".join(current_value).strip()
            current_key, value_part = line.split(":", 1)
            current_key = current_key.lower()
            current_value = [value_part.strip()]
        else:
            current_value.append(line.strip())

    if current_key:
        metadata_dict[current_key.lower()] = " ".join(current_value).strip()

    # Additional processing for "before"
    # Work this into the ``define_judicial_aggregate()`` function
    # Use the list it generates to replace the values in the "written reasons by", "in concurrence", and "in dissent" keys
    # If the decision is written by "The Court", add all the judges to the "concurring" list
    if "before" in metadata_dict:
        before_value = metadata_dict["before"]
        before_list = re.split(
            r"\s*,\s*|\s*\band\b\s*", before_value, flags=re.IGNORECASE
        )

        # Strip whitespace and filter out empty strings
        before_list = [item.strip() for item in before_list if item.strip()]
        before_list = [re.sub(r"\s.*", "", item) for item in before_list]
        metadata_dict["before"] = before_list

    # Classify the judge's appeal position
    opinion_types = ["written reasons by", "in concurrence", "in dissent"]
    for opinion_type in opinion_types:
        define_judicial_aggregate(metadata_dict, opinion_type)

    convert_appeal_heard_date(metadata_dict)
    define_parties(metadata_dict)
    identify_case_type(metadata_dict)

    # Additional processing for "counsel"
    # Turn into a function

    if "counsel" in metadata_dict:
        counsel_value = metadata_dict["counsel"]
        # Regular expression pattern with capturing parentheses to retain delimiters
        delimiters = r"(for|Appellants|Appellant|Respondents|Respondent|own behalf|Intervenor|Court Services)"
        # Splitting the string at delimiters, case insensitive, retaining delimiters
        counsel_list = re.split(delimiters, counsel_value, flags=re.IGNORECASE)

        # Cleaning the list: Removing empty strings, trimming whitespace, removing specific phrases, and replacing "own behalf"
        phrases_to_remove = [
            "for the",
            "appearing on his",
            "appearing on her",
            "on his",
            "on her" ", K.C.,",
            ", Q.C.,",
            ", K.C.",
        ]
        cleaned_counsel_list = []
        for item in counsel_list:
            item = item.strip()
            # Skip the item if it's only "for" or "the"
            if item.lower() in ["for", "the"]:
                continue
            if item:
                for phrase in phrases_to_remove:
                    item = item.replace(phrase, "").strip()
                # Replace "own behalf" with "self-represented"
                item = item.replace("own behalf", "self-represented")
                cleaned_counsel_list.append(item)

        # Update the 'counsel' key in the dictionary
        metadata_dict["counsel"] = cleaned_counsel_list

    # Remove the extraneous "file number" key before returning the dictionary
    metadata_dict.pop("file number", None)

    return metadata_dict


###
# MBCA functions
###


@app.command()
def mbca(file_path: str):
    """
    Processes a markdown file and prints its metadata line by line,
    starting from the first line that begins with the "#" character.

    These steps are specific to SKCA decisions from 2015 to present (2023).

    Args:
        file_path (str): The path to the markdown file.

    """

    metadata_lines = create_metadata_md(file_path)[0]

    # Splits the "File number" and "Citation" lines found in recent SKCA decisions
    for index, item in enumerate(metadata_lines):
        if "number:" in item and "Citation:" in item:
            file_number, citation = item.split("Citation:", 1)

            if "File number:" not in file_number:
                file_number = file_number.replace("number:", "File number:")

            metadata_lines[index] = file_number
            metadata_lines.insert(index + 1, f"Citation:{citation}")

    # Remove the last line if it starts with "#"
    # Then remove the next (reduntant) last line containing the decision's author
    if metadata_lines[-1].startswith("#"):
        metadata_lines = metadata_lines[:-1]
        metadata_lines.pop()
    else:
        metadata_lines.pop()

    # Run the mteadata lines through the processing functions
    metadata_dict = process_metadata_lines(metadata_lines)
    output_file_name = save_metadata_to_json(file_path, metadata_dict)

    typer.echo(f"Metadata exported to JSON file: {output_file_name}")
    typer.echo("Metadata Key-Value Pairs:")
    for key, value in metadata_dict.items():
        typer.echo(f"{key}: {value}")


###
# Functions for exporting metadata to a JSON file, pd dataframe, or CSV file
###


def save_metadata_to_json(file_path: str, metadata_dict: Dict[str, Any]) -> str:
    """
    Saves the metadata dictionary to a JSON file.

    Args:
        file_path (str): The path of the original markdown file.
        metadata_dict (Dict[str, Any]): The metadata dictionary to be saved.

    Returns:
        str: The name of the JSON file where the metadata is saved.
    """
    base_name = os.path.splitext(file_path)[0]
    output_file_name = f"{base_name}.json"

    with open(output_file_name, "w", encoding="utf-8") as json_file:
        json.dump(metadata_dict, json_file, ensure_ascii=False, indent=4)

    return output_file_name


# View a directory and add all files to a list
def view_directories(directories: List[str]) -> List[str]:
    """View all markdown files in a list of directories."""
    files = []
    for directory in directories:
        for file in os.listdir(directory):
            if file.endswith(".md"):
                full_path = os.path.join(directory, file)
                files.append(full_path)

    return files


def generate_dataframe(directories: List[str]) -> pd.DataFrame:
    """Generate a pandas DataFrame from multiple markdown files in multiple directories."""
    files = view_directories(directories)
    metadata_list = []
    for file_path in files:
        metadata = process_metadata_lines(create_metadata_md(file_path)[0])
        if metadata:  # Ensure there is metadata to add
            metadata_list.append(metadata)

    return pd.DataFrame(metadata_list)


@app.command()
def export_to_csv(
    directories: List[str] = typer.Argument(...), output_csv: str = typer.Argument(...)
):
    """
    Export metadata from markdown files in multiple directories to a CSV file.

    Args:
        directories (List[str]): List of directories containing markdown files.
        output_csv (str): Path for the output CSV file.
    """
    df = generate_dataframe(directories)
    df.to_csv(output_csv, index=False)
    typer.echo(f"Data exported to CSV file: {output_csv}")


if __name__ == "__main__":
    app()
