#!/usr/bin/env python3

"""
Rule set for Saskatchewan Court of Appeal decisions from 2015 onward.
"""

# Consider moving these functions to a separate file in the uitls directory

import re

from typing import List
from dateutil.parser import parse

PARTY_ROLES = [
    "Appellants",
    "Appellant",
    "Respondents",
    "Respondent",
    "Intervenors",
    "Intervenor",
    "Applicants",
    "Applicant",
    "Plaintiffs",
    "Plaintiff",
    "Defendants",
    "Defendant",
    "Petitioners",
    "Petitioner",
    "Non-Parties",
    "Non-Party",
    "Non-parties",
    "Non-party",
    "Non Parties",
    "Non Party",
    "Third Parties",
    "Third Party",
    "self-represented",
    "Interested Parties",
    "Interested Party",
]


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

    # Remove "Mr. Justice" and "Madam Justice" from the list items

    if key in metadata_dict:
        value = metadata_dict[key]
        value = [
            item.replace("Mr. Justice", "")
            .replace("Madam Justice", "")
            .replace("Chief Justice", "")
            for item in value
        ]
        metadata_dict[key] = value


def define_parties(metadata_dict: dict) -> None:
    """
    Defines the parties in the metadata dictionary. Designed to work with skca_2015().

    Args:
        metadata_dict (Dict[str, Any]): The metadata dictionary.
    """

    if "between" in metadata_dict:
        # Split the string at the word "And"
        between_value = metadata_dict["between"]
        between_parts = between_value.split("And ")

        # Initialize an empty list to store the results
        between_value = []

        for part in between_parts:
            # Remove underscores and extra spaces
            part = part.replace("_", "").strip()
            # Split each part into party name and party roles
            split_result = split_party_name_and_roles(part, PARTY_ROLES)
            # Only add the split result if it's not already in the list
            if split_result not in between_value:
                between_value.append(split_result)

        # Update the 'between' key in the dictionary
        metadata_dict["between"] = between_value


def split_party_name_and_roles(text, party_roles):
    """
    Splits each text into two parts: party name and party roles.

    Args:
    text (str): The text containing party names and roles.
    party_roles (list): A list of party roles.

    Returns:
    tuple: A tuple with the party name and a string containing all roles.
    """
    # Create a regex pattern to find party roles
    pattern = r"(" + "|".join(re.escape(role) for role in party_roles) + r")"

    # Search for the first occurrence of the pattern
    match = re.search(pattern, text)

    if match:
        # Split the text at the start of the matched role
        index = match.start()
        return text[:index].strip(), text[index:].strip()
    else:
        # No role found, return the whole text as the party name and an empty string for the role
        return text, ""


def identify_case_type(metadata_dict: dict) -> None:
    """
    Examines the "docket" key in the metadata dictionary and identifies the case type. To do so,
    the function checks the first four characters of the docket number. If the first four characters
    are "CACV", the case type is "Civil Appeal". If the first four characters are "CACR", the case
    type is "Criminal Appeal".

    Args:
        metadata_dict (Dict[str, Any]): The metadata dictionary.
    """

    if "file number" in metadata_dict:

        # Split the string at "; " and return a list. If there is no "; ",
        # return the original string as a list item

        file_number_value = metadata_dict["file number"]
        file_number_value = file_number_value.split("; ")
        file_number_value = [item.strip() for item in file_number_value]
        file_number_value = [item for item in file_number_value if item]
        metadata_dict["file number"] = file_number_value

        for item in file_number_value:

            if item.startswith("CACV"):
                metadata_dict["field"] = "civil"
            elif item.startswith("CACR"):
                metadata_dict["field"] = "criminal"
            else:
                pass


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
        (
            r"\b(?:January|February|March|April|May|June|"
            r"July|August|September|October|November|December)\b"
        ),
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
    Saves the result as "case heard" and attaches it to the metadata dictionary.

    Args:
        metadata_dict (Dict[str, Any]): The metadata dictionary.
    """

    if "appeal heard" in metadata_dict:
        appeal_heard_value = metadata_dict["appeal heard"]
        appeal_heard_value = extract_dates(appeal_heard_value)
        metadata_dict["case heard"] = appeal_heard_value
        metadata_dict["case type"] = "appeal"

    if "appeals heard" in metadata_dict:
        appeals_heard_value = metadata_dict["appeals heard"]
        appeals_heard_value = extract_dates(appeals_heard_value)
        metadata_dict["case heard"] = appeals_heard_value
        metadata_dict["case type"] = "appeal"

    if "application heard" in metadata_dict:
        application_heard_value = metadata_dict["application heard"]
        application_heard_value = extract_dates(application_heard_value)
        metadata_dict["case heard"] = application_heard_value
        metadata_dict["case type"] = "application"

    if "applications heard" in metadata_dict:
        applications_heard_value = metadata_dict["applications heard"]
        applications_heard_value = extract_dates(applications_heard_value)
        metadata_dict["case heard"] = applications_heard_value
        metadata_dict["case type"] = "application"

    if "remand heard" in metadata_dict:
        remand_heard_value = metadata_dict["remand heard"]
        remand_heard_value = extract_dates(remand_heard_value)
        metadata_dict["case heard"] = remand_heard_value
        metadata_dict["case type"] = "remand"


def create_metadata_dict(metadata_lines: list) -> dict:
    """
    Creates a metadata dictionary from a list of strings.

    Args:
        metadata_lines (list): A list of strings.

    Returns:
        dict: A dictionary containing the metadata.
    """

    metadata_dict = {}
    current_key = None
    current_value = []

    for index, item in enumerate(metadata_lines):
        # Handling "Between" and "Citation" cases

        if "Between" in item:
            print(metadata_lines[index], metadata_lines[index + 1])
            metadata_lines[index] = item
            print(metadata_lines[index], metadata_lines[index + 1])

        if "number:" in item and "Citation:" in item:
            file_number, citation = item.split("Citation:", 1)
            if "File number:" not in file_number:
                file_number = file_number.replace("number:", "File number:")
            metadata_lines[index] = file_number
            metadata_lines.insert(index + 1, f"Citation:{citation}")

        if "appeal heard" in item:
            metadata_lines[index] = item.replace("appeal heard", "Appeal Heard")

        # Handling URL extraction
        if "<<" in item and ">>" in item:
            start, end = item.find("<<") + 2, item.find(">>")
            metadata_dict["url"] = item[start:end].strip()
            item = item[: start - 2] + item[end + 2 :]

    # Remove the last line if it starts with "#"
    if metadata_lines and metadata_lines[-1].startswith("#"):
        metadata_lines.pop()

    # Remove the last line
    if metadata_lines:
        metadata_lines.pop()

    for index, item in enumerate(metadata_lines):
        # Handling key-value pairs
        if ":" in item:
            if current_key:
                # Special handling for "counsel"
                if current_key.lower() == "counsel":
                    # Join with a semicolon and space
                    joined_value = "; ".join(current_value).strip()

                else:
                    # Regular handling for other keys
                    joined_value = " ".join(current_value).strip()

                metadata_dict[current_key.lower()] = joined_value

            current_key, value_part = item.split(":", 1)
            current_key = current_key.lower()
            current_value = [value_part.strip()]
        else:
            current_value.append(item.strip())

    # Final processing for the last key
    if current_key:
        if current_key.lower() == "counsel":
            joined_value = "; ".join(current_value).strip()
            if joined_value.startswith("; "):
                joined_value = joined_value[2:]
        else:
            joined_value = " ".join(current_value).strip()

        metadata_dict[current_key.lower()] = joined_value

    return metadata_dict


def extract_counsel(metadata_dict: dict) -> None:
    """
    Extracts counsel from the metadata dictionary and saves it as a list of tuples.

    Args:
        metadata_dict (Dict[str, Any]): The metadata dictionary.
    """

    if "counsel" in metadata_dict:
        counsel_value = metadata_dict["counsel"]

        # Split the string on "; " to get individual counsels
        counsel_list = counsel_value.split("; ")

        cleaned_counsel_list = []
        for item in counsel_list:
            # Check for each party role in the counsel string
            for role in PARTY_ROLES:
                if role in item:
                    # Remove the party role from the counsel string
                    item = item.replace(role, "").strip()
                    # Add the party role as an additional list item
                    cleaned_counsel_list.append(role)
                    break  # Stop checking further once a role is found

            item = clean_counsel_entry(item)
            if item:
                cleaned_counsel_list.append(item)

        # Create tuples from the cleaned list
        lawyer_party_tuples = create_lawyer_party_tuples(cleaned_counsel_list)

        # Update the 'counsel' key in the dictionary
        metadata_dict["counsel"] = lawyer_party_tuples


def clean_counsel_entry(entry):
    """
    Cleans a single counsel entry.

    Args:
        entry (str): A counsel entry string.

    Returns:
        str: A cleaned counsel entry.
    """
    phrases_to_remove = [
        "for the",
        "appearing on his",
        "appearing on her",
        "on his",
        "on her",
        ", K.C.,",
        ", Q.C.,",
        ", K.C.",
        ", Q.C.",
        ", QC",
        ", KC",
    ]
    for phrase in phrases_to_remove:
        entry = entry.replace(phrase, "").strip()
    entry = entry.replace("own behalf", "self-represented")
    return entry


def create_lawyer_party_tuples(lawyers_parties_list):
    """
    Creates tuples of lawyers and parties they represent from a list.

    Args:
    lawyers_parties_list (list): A list alternating between lawyers and parties.

    Returns:
    list: A list of tuples with each tuple containing (lawyers, party).
    """
    tuples_list = []

    # Iterate over the list in steps of 2 to pair each lawyer(s) with the corresponding party
    for i in range(0, len(lawyers_parties_list), 2):
        # Check if the next element exists to avoid IndexError
        if i + 1 < len(lawyers_parties_list):
            tuples_list.append((lawyers_parties_list[i], lawyers_parties_list[i + 1]))

    return tuples_list


def skca_2015(metadata_lines: list):
    """
    Processes a markdown file and prints its metadata line by line,
    starting from the first line that begins with the "#" character.

    These steps are specific to SKCA decisions from 2015 to present (2023).

    Args:
        file_path (str): The path to the markdown file.

    """

    metadata_dict = create_metadata_dict(metadata_lines)


    if "before" in metadata_dict:
        before_value = metadata_dict["before"]
        before_list = re.split(
            r"\s*,\s*|\s*\band\b\s*", before_value, flags=re.IGNORECASE
        )

        # Strip whitespace and filter out empty strings
        before_list = [item.strip() for item in before_list if item.strip()]
        before_list = [re.sub(r"\s.*", "", item) for item in before_list]

        # Remove an item if it only contains "J.A." or "C.J.S."
        before_list = [item for item in before_list if item not in ["J.A.", "C.J.S.", "JA", "CJS"]]

        metadata_dict["before"] = before_list

    # Classify the judge's appeal position
    opinion_types = [
        "written reasons by",
        "in concurrence",
        "in dissent",
        "concurring reasons by",
    ]
    for opinion_type in opinion_types:
        define_judicial_aggregate(metadata_dict, opinion_type)

    convert_appeal_heard_date(metadata_dict)
    define_parties(metadata_dict)
    identify_case_type(metadata_dict)
    extract_counsel(metadata_dict)

    return metadata_dict
