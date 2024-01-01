#!/usr/bin/env python3

"""
Rule set for Saskatchewan Court of Appeal decisions from 2015 onward.
"""

# Consider moving these functions to a separate file in the uitls directory

import re

from typing import List
from dateutil.parser import parse

PARTY_ROLES = [
    "Proposed Intervenors",
    "Proposed Intervenor",
    "Prospective Appellants",
    "Prospective Appellant",
    "Prospective Respondents",
    "Prospective Respondent",
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


def define_judicial_aggregate(metadata_dict: dict) -> None:
    """
    Defines a judicial aggregate in the metadata dictionary. Designed to work with skca_2015().

    Args:
        metadata_dict (Dict[str, Any]): The metadata dictionary.
    """

    opinion_types = [
        "written reasons by",
        "majority reasons by",
        "majority reasons",
        "dissenting reasons by",
        "dissenting reasons",
        "minority reasons by",
        "minority reasons",
        "concurring reasons by",
        "concurring reasons",
        "in concurrence",
        "in dissent",
        "by",
    ]

    standardized_roles = {
        "written reasons by": "reasons",
        "majority reasons by": "reasons",
        "majority reasons": "reasons",
        "dissenting reasons by": "dissenting reasons",
        "dissenting reasons": "dissenting reasons",
        "minority reasons by": "dissenting reasons",
        "minority reasons": "dissenting reasons",
        "concurring reasons by": "concurring reasons",
        "concurring reasons": "concurring reasons",
        "in concurrence": "concurring",
        "in dissent": "dissenting",
        "by": "reasons"
    }

    split_pattern = "The Honourable "
    justice_titles = ["Mr. Justice", "Madam Justice", "Chief Justice"]

    for key in opinion_types:
        if key in metadata_dict:
            value = metadata_dict[key]
            value = value.split(split_pattern)
            value = [item.strip() for item in value if item]

            # Creating tuples of (judge's name, standardized role)
            processed_values = []
            for item in value:
                for title in justice_titles:
                    item = item.replace(title, "").strip()
                item = item.replace("and", "").strip()
                standardized_role = standardized_roles.get(key, key)
                processed_values.append((item, standardized_role))

            metadata_dict[key] = processed_values
        else:
            metadata_dict[key] = []


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
        processed_parties = []

        for part in between_parts:
            # Remove underscores and extra spaces
            part = part.replace("_", "").strip()

            # Split each part into party name and party roles
            split_results = split_party_name_and_roles(part, PARTY_ROLES)

            for split_result in split_results:
                # Only add the split result if it's not already in the list
                if split_result not in processed_parties:
                    processed_parties.append(split_result)

        # Update the 'between' key in the dictionary
        metadata_dict["between"] = processed_parties


def define_coram(metadata_dict: dict) -> None:
    """
    Identifies the judges who heard the case and saves them as a list in the metadata dictionary.
    Although the judges so defined a

    Args:
        metadata_dict (Dict[str, Any]): The metadata dictionary.
    """

    if "before" in metadata_dict:
        before_value = metadata_dict["before"]
        before_list = re.split(
            r"\s*,\s*|\s*\band\b\s*", before_value, flags=re.IGNORECASE
        )

        # Strip whitespace and filter out empty strings
        before_list = [item.strip() for item in before_list if item.strip()]
        before_list = [re.sub(r"\s.*", "", item) for item in before_list]

        # Remove an item if it only contains "J.A." or "C.J.S."
        before_list = [
            item
            for item in before_list
            if item not in ["J.A.", "C.J.S.", "JA", "CJS", "C.J.S", "JJ.A."]
        ]

        metadata_dict["before"] = before_list


def split_party_name_and_roles(text, party_roles):
    """
    Splits each text into two parts: party names and party roles.
    Additionally, splits multiple party names in a single string.

    Args:
        text (str): The text containing party names and roles.
        party_roles (list): A list of party roles.

    Returns:
        list: A list of tuples, each containing a party name and a string containing the role.
    """
    # Create a regex pattern to find party roles
    pattern = r"(" + "|".join(re.escape(role) for role in party_roles) + r")"

    # Search for the first occurrence of the pattern
    match = re.search(pattern, text)

    if match:
        # Split the text at the start of the matched role
        index = match.start()
        party_names = text[:index].strip()
        role = text[index:].strip()

        # Split multiple party names
        split_names = re.split(r",\s*and\s*|,\s*|\s*and\s+", party_names)
        print(split_names)

        return [(name.strip(), role) for name in split_names]
    else:
        # No role found, return the whole text as the party name and an empty string for the role
        return [(text, "")]



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


def extract_other_citations(metadata_dict: dict) -> None:
    """
    Extracts other citations from the metadata dictionary and saves them as a list.

    Args:
        metadata_dict (Dict[str, Any]): The metadata dictionary.
    """

    if "other citation" in metadata_dict:
        other_citations_value = metadata_dict["other citation"]
        other_citations_value = other_citations_value.split("-- ")
        other_citations_value = [item.strip() for item in other_citations_value]
        other_citations_value = [item for item in other_citations_value if item]
        metadata_dict["other citations"] = other_citations_value

    elif "other citations" in metadata_dict:
        other_citations_value = metadata_dict["other citations"]
        other_citations_value = other_citations_value.split("-- ")
        other_citations_value = [item.strip() for item in other_citations_value]
        other_citations_value = [item for item in other_citations_value if item]
        metadata_dict["other citations"] = other_citations_value


def convert_appeal_heard_date(metadata_dict: dict) -> None:
    """
    Converts the "appeal heard" key in the metadata dictionary to a list of dates in YYYY-MM-DD
    format, or saves it as a single-item list containing the original string if formatting fails.
    Saves the result as "case heard" and attaches it to the metadata dictionary.

    Args:
        metadata_dict (Dict[str, Any]): The metadata dictionary.
    """

    heard_keys = {
        "appeal heard": "appeal",
        "appeals heard": "appeal",
        "application heard": "application",
        "applications heard": "application",
        "application considered": "application",
        "applications considered": "application",
        "remand heard": "remand",
        "chambers date": "application",
        "heard": "case",
    }

    for key, case_type in heard_keys.items():
        if key in metadata_dict:
            heard_value = metadata_dict[key]
            heard_value = extract_dates(heard_value)
            metadata_dict["case heard"] = heard_value
            metadata_dict["case type"] = case_type
            break  # Assumes only one key is present, remove if multiple keys can be present


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
            metadata_lines[index] = item

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

    def process_counsel_text(item, split_str, replacement_str="Self-represented"):
        temp_list = item.split(split_str)
        return [
            replacement_str if x.strip() == "own behalf" else x.strip()
            for x in temp_list
        ]

    if "counsel" in metadata_dict:
        counsel_value = metadata_dict["counsel"]

        # Split the string on "; " to get individual counsels
        counsel_list = counsel_value.split("; ")
        refined_counsel_list = []

        for item in counsel_list:

            if "for" in item:
                temp_list = item.split("for")
                temp_list.reverse()
                refined_counsel_list.extend([x.strip() for x in temp_list])
            elif any(
                phrase in item
                for phrase in [
                    "appearing on his ",
                    "appearing on her ",
                    "appearing on their ",
                    "on their ",
                    "on his",
                    "on her",
                ]
            ):
                match_phrases = [
                    "appearing on his ",
                    "appearing on her ",
                    "appearing on their ",
                    "on their ",
                    "on his",
                    "on her",
                ]
                for phrase in match_phrases:
                    if phrase in item:
                        refined_counsel_list.extend(process_counsel_text(item, phrase))
                        break
            else:
                refined_counsel_list.append(item.strip())

        # Further processing of refined_counsel_list
        cleaned_counsel_list = process_counsel_list(refined_counsel_list)

        # Update the 'counsel' key in the dictionary
        metadata_dict["counsel"] = create_lawyer_party_tuples(cleaned_counsel_list)


def process_counsel_list(counsel_list):
    cleaned_counsel_list = []
    for item in counsel_list:
        for role in PARTY_ROLES:
            if role in item:
                item = item.split(role)[0].strip()
                cleaned_counsel_list.append(role)
                break
        item = clean_counsel_entry(item)
        if item not in ["the", "and", "The", "And", ""]:
            cleaned_counsel_list.append(item)
    return cleaned_counsel_list


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
        ", K.C",
        ", Q.C",
        ", QC",
        ", KC",
        " Q.C.",
        " K.C.",
        "the , ",
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
            # Split the string at ", and " or ", and" or ",and " or ",and"
            tuples_list.append(
                (
                    lawyers_parties_list[i],
                    re.split(r",\s*and\s*|\sand\s*|,\s*", lawyers_parties_list[i + 1]),
                )
            )

    return tuples_list


def skca_2015(metadata_lines: list):
    """
    Extracts metadata from a Saskatchewan Court of Appeal decision from 2015 onward.

    Args:
        file_path (str): The path to the markdown file.

    """

    metadata_dict = create_metadata_dict(metadata_lines)

    define_judicial_aggregate(metadata_dict)
    extract_other_citations(metadata_dict)
    define_coram(metadata_dict)
    convert_appeal_heard_date(metadata_dict)
    define_parties(metadata_dict)
    identify_case_type(metadata_dict)
    extract_counsel(metadata_dict)

    if "disposition" in metadata_dict:
        # Split the string at "; " and return a list. If there is no "; ",
        # return the original string as a list item
        disposition_value = metadata_dict["disposition"]
        disposition_value = disposition_value.split("; ")
        disposition_value = [item.strip() for item in disposition_value]
        disposition_value = [item for item in disposition_value if item]

        # Update the 'disposition' key in the dictionary
        metadata_dict["disposition"] = disposition_value

    if "on appeal from" in metadata_dict:
        # Split the string at "," and return a list.
        # If there are more than two items, recombine all but the last item
        # and append the recombined string to the top of the list.
        # Return two items
        on_appeal_from_value = metadata_dict["on appeal from"]
        on_appeal_from_value = on_appeal_from_value.split(", ")
        if len(on_appeal_from_value) > 2:
            on_appeal_from_value = [
                ", ".join(on_appeal_from_value[:-1]),
                on_appeal_from_value[-1],
            ]
        on_appeal_from_value = [item.strip() for item in on_appeal_from_value]
        on_appeal_from_value = [item for item in on_appeal_from_value if item]
        # Remove the string "J.C. of " if it exists in the second item
        if len(on_appeal_from_value) > 1 and "J.C. of " in on_appeal_from_value[1]:
            on_appeal_from_value[-1] = on_appeal_from_value[-1].replace("J.C. of ", "")

        metadata_dict["on appeal from"] = on_appeal_from_value

    if "on application from" in metadata_dict:
        # Split the string at "," and return a list.
        # If there are more than two items, recombine all but the last item
        # and append the recombined string to the top of the list.
        # Return two items
        on_appeal_from_value = metadata_dict["on application from"]
        on_appeal_from_value = on_appeal_from_value.split(", ")
        if len(on_appeal_from_value) > 2:
            on_appeal_from_value = [
                ", ".join(on_appeal_from_value[:-1]),
                on_appeal_from_value[-1],
            ]
        on_appeal_from_value = [item.strip() for item in on_appeal_from_value]
        on_appeal_from_value = [item for item in on_appeal_from_value if item]
        metadata_dict["on appeal from"] = on_appeal_from_value

    return metadata_dict


def skca_2015_instructions(context, metadata_lines):

    context["rules_exist"] = "SKCA 2015 rules"
    case_dict = skca_2015(metadata_lines)

    # Use .get() method to safely access dictionary keys
    context["short_url"] = case_dict.get("url", "")
    context["before"] = case_dict.get("before", [])
    context["case_type"] = (
        case_dict.get("case type", ""),
        case_dict.get("field", ""),
    )
    context["file_number"] = case_dict.get("file number", "")
    context["written_reasons"] = case_dict.get("written reasons by", [])
    context["majority_reasons"] = case_dict.get("majority reasons by", [])
    context["minority_reasons"] = case_dict.get("minority reasons by", [])
    context["dissenting_reasons"] = case_dict.get("dissenting reasons by", [])
    context["concurring_reasons"] = case_dict.get("concurring reasons by", [])
    context["majority"] = case_dict.get("majority", [])
    context["minority"] = case_dict.get("minority", [])
    context["concurring"] = case_dict.get("in concurrence", [])
    context["dissenting"] = case_dict.get("in dissent", [])
    context["disposition"] = case_dict.get("disposition", "")
    context["parties"] = case_dict.get("between", [])
    context["counsel"] = case_dict.get("counsel", [])
    context["case_heard"] = case_dict.get("case heard", "")
    context["other_citations"] = case_dict.get("other citations", [])
    context["disposition_value"] = case_dict.get("disposition", "")
    context["appeal_from"] = case_dict.get("on appeal from", "")
