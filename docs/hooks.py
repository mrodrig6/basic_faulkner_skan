"""Render the repository README as the site homepage without a second copy."""

from pathlib import Path
import re

from mkdocs.structure.files import File


def on_files(files, config):
    """Add a virtual homepage and the verbatim repository license asset."""
    root = Path(config.config_file_path).parent
    files.append(File.generated(config, "index.md", content=(root / "README.md").read_text(encoding="utf-8")))
    files.append(File.generated(config, "license.txt", content=(root / "LICENSE").read_text(encoding="utf-8")))
    return files


def on_page_markdown(markdown, page, **kwargs):
    """Translate only homepage links from repository paths to docs paths."""
    if page.file.src_uri != "index.md":
        return markdown
    markdown = re.sub(r"(?<=\]\()docs/", "", markdown)
    return re.sub(r"(?<=\]\()LICENSE(?=\))", "license.txt", markdown)
