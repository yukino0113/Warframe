def strip_text(text):
    return text.getText().strip()

def check_empty_row(row):
    return row.get('class') and 'blank-row' in row.get('class')