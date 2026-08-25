#!/usr/bin/env python3
"""Validate generated local references and SVG assets."""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ElementTree
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit


REFERENCE_ATTRIBUTES = {"href", "src"}
SCRATCH_NAMES = {
    "WARNINGS",
    "images.aux",
    "images.log",
    "images.out",
    "images.pdf",
    "images.pl",
    "images.tex",
    "internals.pl",
    "labels.pl",
}


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.anchors: set[str] = set()
        self.references: list[tuple[int, str, str]] = []

    def handle_starttag(
        self, tag: str, attributes: list[tuple[str, str | None]]
    ) -> None:
        self._record(tag, attributes)

    def handle_startendtag(
        self, tag: str, attributes: list[tuple[str, str | None]]
    ) -> None:
        self._record(tag, attributes)

    def _record(
        self, tag: str, attributes: list[tuple[str, str | None]]
    ) -> None:
        line, _ = self.getpos()
        for name, value in attributes:
            normalized_name = name.lower()
            if value is None:
                continue
            if normalized_name == "id" or (
                tag.lower() == "a" and normalized_name == "name"
            ):
                self.anchors.add(value)
            if normalized_name in REFERENCE_ATTRIBUTES:
                self.references.append((line, normalized_name, value))


def parse_html(path: Path) -> DocumentParser:
    parser = DocumentParser()
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    return parser


def local_target(root: Path, page: Path, reference: str) -> tuple[Path, str] | None:
    normalized_reference = reference.strip()
    parsed = urlsplit(normalized_reference)
    if parsed.scheme or parsed.netloc or normalized_reference.startswith("//"):
        return None

    decoded_path = unquote(parsed.path)
    if decoded_path.startswith("/"):
        target = root / decoded_path.lstrip("/")
    elif decoded_path:
        target = page.parent / decoded_path
    else:
        target = page

    target = target.resolve()
    if decoded_path.endswith("/") or target.is_dir():
        target /= "index.html"
    return target, unquote(parsed.fragment)


def main() -> int:
    if len(sys.argv) != 2:
        print(f"Usage: {Path(sys.argv[0]).name} PUBLIC_DIRECTORY", file=sys.stderr)
        return 2

    root = Path(sys.argv[1]).resolve()
    if not root.is_dir():
        print(f"Generated site directory does not exist: {root}", file=sys.stderr)
        return 2

    html_paths = sorted(root.rglob("*.html"))
    svg_paths = sorted(root.rglob("*.svg"))
    documents: dict[Path, DocumentParser] = {}
    errors: list[str] = []
    local_reference_count = 0

    for path in html_paths:
        if not path.stat().st_size:
            errors.append(f"{path.relative_to(root)}: empty HTML document")
            continue
        try:
            documents[path.resolve()] = parse_html(path)
        except (OSError, UnicodeError) as error:
            errors.append(f"{path.relative_to(root)}: cannot parse HTML: {error}")

    for page, document in list(documents.items()):
        for line, attribute, reference in document.references:
            resolved = local_target(root, page, reference)
            if resolved is None:
                continue
            local_reference_count += 1
            target, fragment = resolved
            try:
                target.relative_to(root)
            except ValueError:
                errors.append(
                    f"{page.relative_to(root)}:{line}: {attribute} escapes public/: "
                    f"{reference}"
                )
                continue
            if not target.is_file():
                errors.append(
                    f"{page.relative_to(root)}:{line}: missing {attribute} target: "
                    f"{reference}"
                )
                continue
            if fragment and target.suffix.lower() in {".htm", ".html"}:
                target_document = documents.get(target.resolve())
                if target_document is None:
                    try:
                        target_document = parse_html(target)
                        documents[target.resolve()] = target_document
                    except (OSError, UnicodeError) as error:
                        errors.append(
                            f"{page.relative_to(root)}:{line}: cannot inspect fragment "
                            f"target {reference}: {error}"
                        )
                        continue
                if fragment not in target_document.anchors:
                    errors.append(
                        f"{page.relative_to(root)}:{line}: missing fragment target: "
                        f"{reference}"
                    )

    for path in svg_paths:
        try:
            ElementTree.parse(path)
        except (ElementTree.ParseError, OSError) as error:
            errors.append(f"{path.relative_to(root)}: invalid SVG XML: {error}")

    for path in root.rglob("*"):
        if path.is_file() and (
            path.name in SCRATCH_NAMES or path.name.startswith(".latex2html-")
        ):
            errors.append(f"{path.relative_to(root)}: converter scratch file remains")

    if errors:
        print("Generated-site validation failed:", file=sys.stderr)
        for error in sorted(errors):
            print(f"  - {error}", file=sys.stderr)
        return 1

    print(
        f"Checked {len(html_paths)} HTML pages, {len(svg_paths)} SVG assets, "
        f"and {local_reference_count} local references"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
