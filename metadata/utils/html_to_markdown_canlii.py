#!/usr/bin/env python3

import re
import os
import shutil
import glob
import html2text
import typer

from typing import List

app = typer.Typer()

UNWANTED_PATTERNS = [
    r"\[ !\[CanLII Logo\]\(.+?\) \]\(.+?\)",
    r"\[Home\]\(.+?\) › .+?CanLII\)",
    r"Loading paragraph markers __",
    r"\* Document",
    r"\* History  __",
    r"\* Cited documents  __",
    r"\* Treatment  __",
    r"\* CanLII Connects  __",
    r"Citations  __",
    r"Discussions  __",
    r"Unfavourable mentions  __",
    r"\nExpanded Collapsed\n",
]

HTML2TEXT_HANDLER = html2text.HTML2Text()
HTML2TEXT_HANDLER.ignore_links = False

DATE_PATTERN = re.compile(r"Date:\s*\n")
FILE_NUMBER_PATTERN = re.compile(r"File number:\s*\n")
CITATION_PATTERN = re.compile(r"Citation:\s*\n")
TABLE_PATTERN = re.compile(r"---(\|---)+")
FOOTER_PATTERN = re.compile(r"Back to top.*$", re.DOTALL)


def html_to_markdown(html_content: str) -> str:
    """..."""
    return HTML2TEXT_HANDLER.handle(html_content)


def convert_file(html_filepath: str, markdown_filepath: str) -> None:
    """
    Converts an HTML file to a markdown file.

    Args:
        html_filepath (str): Path to the input HTML file.
        markdown_filepath (str): Path to the output markdown file.
    """

    with open(html_filepath, "r", encoding="utf-8") as file:
        html_content = file.read()

    markdown_content = html_to_markdown(html_content)
    refined_markdown_content = refine_markdown(markdown_content)

    with open(markdown_filepath, "w", encoding="utf-8") as file:
        file.write(refined_markdown_content)


def refine_markdown(
    md_content: str, unwanted_patterns: List[str] = UNWANTED_PATTERNS
) -> str:
    """..."""

    md_content = md_content.replace("## ", "# ", 1)
    md_content = DATE_PATTERN.sub("Date: ", md_content)
    md_content = FILE_NUMBER_PATTERN.sub("File number: ", md_content)
    md_content = CITATION_PATTERN.sub("Citation: ", md_content)

    for pattern_str in unwanted_patterns:
        pattern = re.compile(pattern_str)
        md_content = pattern.sub("", md_content)

    md_content = FOOTER_PATTERN.sub("", md_content)
    md_content = TABLE_PATTERN.sub("\n", md_content)
    md_content = md_content.replace("|", "\n")
    md_content = md_content.replace("[__  PDF]", "[PDF]")

    return md_content.strip()


def create_directories(base_directory):
    """Create 'html' and 'md' directories."""
    html_dir = os.path.join(base_directory, "html")
    md_dir = os.path.join(base_directory, "md")
    os.makedirs(html_dir, exist_ok=True)
    os.makedirs(md_dir, exist_ok=True)
    return html_dir, md_dir


@app.command()
def convert_all_html_to_markdown(
    directory: str = typer.Argument(os.getcwd(), help="Directory containing HTML files")
):
    """Converts all HTML files in the given directory to Markdown and sorts them."""
    html_dir, md_dir = create_directories(directory)

    for html_file in glob.glob(os.path.join(directory, "*.html")):
        # Define new paths
        new_html_path = os.path.join(html_dir, os.path.basename(html_file))
        markdown_file = os.path.basename(html_file).rsplit(".", 1)[0] + ".md"
        markdown_path = os.path.join(md_dir, markdown_file)

        # Convert and move files
        convert_file(html_file, markdown_path)
        shutil.move(html_file, new_html_path)

        print(f"Converted and moved {html_file} to {markdown_path}")


def main():
    app()


if __name__ == "__main__":
    main()
