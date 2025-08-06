from bs4.element import Tag


def strip_text(text: Tag) -> str:
    return text.getText().strip()


def is_empty_row(row: Tag) -> bool:
    return row.get('class') and 'blank-row' in row.get('class')