#!/usr/bin/env python3

"""
Rules for extracting metadata from any CanLII case.
"""

import re

from bs4 import BeautifulSoup

from ..utils.jurisdiction import (
    define_jurisprudential_network,
    define_legislative_network,
)

def create_primary_key(citation):
    """
    Creates a file path from a citation.
    """

    # Extract the primary key. This is the file name, minus the extension
    primary_key = citation.split("/")[-1].split(".")[0]

    return primary_key

def extract_citations(html_content):
    """
    Searches the HTML document for judgmelsntLinks and legislationLinks and returns a list of
    citations.
    judgmentLinks are stored in the div tag <DIV ID="judgmentLinks" STYLE="display: none;">
    legislationLinks are stored in the div tag <DIV ID="legislationLinks" STYLE="display: none;">
    """

    # Extracting judgmentLinks
    soup = BeautifulSoup(html_content, "html.parser")

    # Find the 'judgmentLinks' div
    judgment_links_div = soup.find("div", id="judgmentLinks")
    # Find all 'li' elements within the 'judgmentLinks' div and extract 'data-path', excluding
    # 'reflex'
    # Handle in case there is no 'judgmentLinks' div
    if judgment_links_div:
        case_paths = [
            li["data-path"]
            for li in judgment_links_div.find_all("li")
            if "data-path" in li.attrs and "reflex" not in li["data-path"]
        ]
    else:
        case_paths = ["None"]

    # Run the judgment_links through the define_jurisprudential_network function
    case_paths = define_jurisprudential_network(case_paths)

    # Extracting legislationLinks
    legislation_links_div = soup.find("div", id="legislationLinks")
    # Find all 'li' elements within the 'legislationLinks' div and extract 'data-path', excluding
    # 'reflex'. Handle in case there is no 'legislationLinks' div
    if legislation_links_div:
        legislation_paths = [
            li["data-path"]
            for li in legislation_links_div.find_all("li")
            if "data-path" in li.attrs and "reflex" not in li["data-path"]
        ]
    else:
        legislation_paths = ["None"]
    # Remove duplicates
    legislation_paths = define_legislative_network(list(set(legislation_paths)))

    return case_paths, legislation_paths

def extract_general_metadata(submitted_text, context):
    """
    Extracts general metadata from the HTML document.
    Move to the rules module.
    """

    context["case_links"] = extract_citations(submitted_text)[0]
    context["legislation_links"] = extract_citations(submitted_text)[1]

    # Verify that the required metadata is available
    style_of_cause_match = re.search(
        r'<meta name="lbh-title" content="([^"]+)"', submitted_text
    )
    citation_match = re.search(
        r'<meta name="lbh-citation" content="([^"]+)"', submitted_text
    )
    decision_date_match = re.search(
        r'<meta name="lbh-decision-date" content="([^"]+)"', submitted_text
    )
    language_match = re.search(
        r'<meta name="lbh-lang" content="([^"]+)"', submitted_text
    )
    court_level_match = re.search(
        r'<meta name="lbh-collection" content="([^"]+)"', submitted_text
    )
    jurisdiction_match = re.search(
        r'<meta name="lbh-jurisdiction" content="([^"]+)"', submitted_text
    )
    keywords_match = re.search(
        r'<meta name="lbh-keywords" content="([^"]+)"', submitted_text
    )
    subjects_match = re.search(
        r'<meta name="lbh-subjects" content="([^"]+)"', submitted_text
    )
    url_match = re.search(
        r'<meta name="lbh-document-url" content="([^"]+)"', submitted_text
    )

    # Returns the uncomplicated case information
    if (
        style_of_cause_match
        and citation_match
        and decision_date_match
        and url_match
        and court_level_match
        and jurisdiction_match
    ):
        style_of_cause = style_of_cause_match.group(1)
        citation = citation_match.group(1).replace("(CanLII)", "").strip()

        context["style_of_cause"] = style_of_cause
        context["citation"] = citation
        context["decision_year"] = citation[:4]
        context["decision_date"] = decision_date_match.group(1)
        context["url"] = url_match.group(1)
        context["primary_key"] = create_primary_key(url_match.group(1))
        context["court_level"] = court_level_match.group(1)
        context["jurisdiction"] = jurisdiction_match.group(1)
        context["case_info_available"] = True

    else:
        context["case_info_available"] = False

    # Checks language to determine whether the case is in English or French
    if language_match:
        if language_match.group(1) == "en":
            context["language"] = "English"
        elif language_match.group(1) == "fr":
            context["language"] = "French"
    else:
        context["language"] = "None"

    # Checks for CanLII keywords and places them into a list
    if keywords_match:
        keywords_string = keywords_match.group(1)
        # Splitting at either "—" or "|"
        keywords_list = re.split(r"—|\|", keywords_string)
        context["keywords_list"] = [keyword.strip() for keyword in keywords_list]
        # Remove duplicates
        context["keywords_list"] = list(set(context["keywords_list"]))
    else:
        context["keywords"] = "None"

    # Checks for case subjects and places them into a list
    if subjects_match:
        subjects_string = subjects_match.group(1)
        # Checking for separators and splitting if they exist
        if "—" in subjects_string or "|" in subjects_string:
            subjects_list = re.split(r"—|\|", subjects_string)
        else:
            subjects_list = [subjects_string]  # No separator, treat as single item
        context["subjects_list"] = [subject.strip() for subject in subjects_list]

    else:
        context["subjects"] = "None"
