"""
Django views for the basic canlii_analytics app.
"""

import re
import os
from django.shortcuts import render
from bs4 import BeautifulSoup

from .utils.html_to_markdown_canlii import (
    convert_file,
    html_to_markdown,
    refine_markdown,
)
from .utils.jurisdiction import (
    define_jurisprudential_network,
    define_legislative_network,
)
from .utils.markdown import process_markdown

from .rules.skca_2015 import skca_2015


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


def create_primary_key(citation):
    """
    Creates a file path from a citation.
    """

    # Extract the primary key. This is the file name, minus the extension
    primary_key = citation.split("/")[-1].split(".")[0]

    return primary_key


def save_file(request, submitted_text, context, url):
    """
    Saves the file to disk. If no file path is provided, the default file path is used.
    Future versions will save the output as a JSON file, rather than saving HTML/Markdown files
    to disk.
    """
    file_path = request.POST.get("filePath")
    if not file_path:
        jurisdiction = url.split("/")[4]
        court_level = url.split("/")[5]
        decision_year = url.split("/")[7]
        primary_key = url.split("/")[8]
        file_path = (
            f"../canlii_data/{jurisdiction}/"
            f"{court_level}/{decision_year}/"
            f"{primary_key}/{primary_key}.html"
        )

    # Create directory if it doesn't exist
    directory = os.path.dirname(file_path)
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
        except OSError as e:
            context["message"] = f"An error occurred while creating the directory: {e}"
            return render(request, "index.html", context)

    # Save the HTML file
    try:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(submitted_text)
        context["file_saved"] = True
        context["file_path"] = file_path
        context["message"] = "File written."
    except IOError as e:
        context["message"] = f"An error occurred while writing the file: {e}"
        return render(request, "index.html", context)

    # Convert and save as Markdown
    markdown_file_path = os.path.splitext(file_path)[0] + ".md"
    try:
        convert_file(file_path, markdown_file_path)
        context["message"] = f"File successfully written to {file_path}.md"
    except IOError as e:
        context["message"] += f" | An error occurred while converting to Markdown: {e}"

    return render(request, "index.html", context)


def extract_general_metadata(submitted_text, context):
    """
    Extracts general metadata from the HTML document.
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

def process_main_content(main_content):
    """
    Processes the main content of the markdown file.
    """

    # Split the main_content string whenever the pattern "\n__\n" is found
    # This will split the main_content into paragraphs
    paragraphs = main_content.split("\n__\n")
    print(len(paragraphs))
    for paragraph in paragraphs:
        # Remove any leading or trailing whitespace
        paragraph = paragraph.strip()
        # Remove any leading or trailing newlines
        paragraph = paragraph.replace("\n", " ")

        # Replace "]               " with "] "
        paragraph = re.sub(r"\]\s+", "] ", paragraph)

        print(paragraph)


def index(request):
    """
    The main view for the canlii_analytics app.
    """
    context = {}
    if request.method == "POST":
        submitted_text = request.POST.get("textfield")

        # Extract general metadata
        extract_general_metadata(submitted_text, context)

        # Save the file to disk if the saveFile checkbox is checked
        if "saveFile" in request.POST:  # Check if the save file box is checked
            save_file(request, submitted_text, context, context.get("url", ""))

        # Court-specific metadata extraction and cleaning

        # Create a markdown file for jurisdiction-specific analysis
        markdown_content = html_to_markdown(submitted_text)
        refined_markdown_content = refine_markdown(markdown_content)

        # Extract the headnote, file content and assign to context
        metadata_lines, main_content = process_markdown(refined_markdown_content)
        process_main_content(main_content)
        context["headnote"] = metadata_lines

        # Check to see if any special rules apply
        # Will need to be replaced with an extensible solution once more rules are added

        context["rules"] = "default"
        if (
            context["jurisdiction"] == "Saskatchewan"
            and int(context["decision_year"]) >= 2016
        ):
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
            context["concurring"] = case_dict.get("in concurrence", [])
            context["dissenting"] = case_dict.get("in dissent", [])
            context["concurring_reasons"] = case_dict.get("concurring reasons by", [])
            context["disposition"] = case_dict.get("disposition", "")
            context["parties"] = case_dict.get("between", [])
            context["counsel"] = case_dict.get("counsel", [])
            context["case_heard"] = case_dict.get("case heard", "")

    return render(request, "index.html", context)
