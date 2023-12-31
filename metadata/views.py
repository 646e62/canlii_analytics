"""
Django views for the basic canlii_analytics app.
"""

import re
import os
from django.shortcuts import render

from .utils.html_to_markdown_canlii import (
    convert_file,
    html_to_markdown,
    refine_markdown,
)

from .utils.markdown import process_markdown

from .rules.skca_2003 import skca_2003_instructions
from .rules.skca_2015 import skca_2015_instructions
from .rules.general import extract_general_metadata


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
        context["message"] = f"Source code for {primary_key} backed up locally."
    except IOError as e:
        context["message"] += f" | An error occurred while converting to Markdown: {e}"

    return render(request, "index.html", context)


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


def index(request):
    """
    The main view for the canlii_analytics app.
    """
    context = {}
    if request.method == "POST":
        submitted_text = request.POST.get("textfield")

        # Extract general metadata from HTML using the general rule set
        extract_general_metadata(submitted_text, context)

        # Save the file to disk if the saveFile checkbox is checked
        if "saveFile" in request.POST:  # Check if the save file box is checked
            save_file(request, submitted_text, context, context.get("url", ""))

        # Create a markdown file for jurisdiction-specific analysis
        markdown_content = html_to_markdown(submitted_text)
        refined_markdown_content = refine_markdown(markdown_content)

        # Extract the headnote, file content and assign to context
        metadata_lines, main_content = process_markdown(refined_markdown_content)
        process_main_content(main_content)
        context["headnote"] = metadata_lines

        # Check to see if any special rules apply
        # Saskatchewan Court of Appeal 2015 rules
        context["rules"] = "default"
        if (
            context["jurisdiction"] == "Saskatchewan"
            and int(context["decision_year"]) >= 2016
        ):
            skca_2015_instructions(context, metadata_lines)
            context["rules"] = "skca_2015"

        if context["jurisdiction"] == "Saskatchewan" and int(context["decision_year"]) == 2015:
            context["rules"] = "skca_2003, skca_2015"
            skca_2015_instructions(context, metadata_lines)
            # Check if 'before' section is empty. If so, use the 2003 rules
            if not context["before"]:
                skca_2003_instructions(context, metadata_lines)
                context["rules"] = "skca_2003"
            else:
                context["rules"] = "skca_2015"

        if context["jurisdiction"] == "Saskatchewan" and int(context["decision_year"]) <= 2014 and int(context["decision_year"]) >= 2003:
            skca_2003_instructions(context, metadata_lines)
            context["rules"] = "skca_2003"

    return render(request, "index.html", context)
