import json
from typing import Any, List, Optional, TypedDict

import click
from pypdf import PdfReader


class TocItem(TypedDict):
    title: str
    page: int
    children: List["TocItem"]


@click.command()
@click.argument("pdf_path")
def main(pdf_path: str) -> None:
    reader: PdfReader = PdfReader(pdf_path)
    outlines: List[Any] = reader.outline

    def parse_outline(outlines: List[Any]) -> List[TocItem]:
        result: List[TocItem] = []
        i = 0
        while i < len(outlines):
            item = outlines[i]
            if isinstance(item, list):
                # Children of the previous item
                if result:
                    result[-1]["children"] = parse_outline(item)
                i += 1
            else:
                page_num: Optional[int] = reader.get_page_number(item.page)
                page: int = (page_num + 1) if page_num is not None else 0
                result.append(
                    TocItem(
                        title=item.title,
                        page=page,
                        children=[],
                    )
                )
                i += 1
        return result

    toc: List[TocItem] = parse_outline(outlines)
    with open("toc.json", "w") as f:
        json.dump(toc, f, indent=2)


if __name__ == "__main__":
    main()
