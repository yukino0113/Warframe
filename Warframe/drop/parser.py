import requests
from bs4 import BeautifulSoup
from icecream import ic


class Parser:
    def __init__(self):
        self.response = requests.get('https://www.warframe.com/zh-hant/droptables')
        self.status = self.response.status_code
        self.content = self.response.text

Parser()

"""
    soup = BeautifulSoup(page_content, 'html.parser')
    tables = soup.find_all('table', class_='drop-table')

    for table in tables:
        # Example: Extract the table headers
        headers = [header.text for header in table.find_all('th')]
        print("Headers:", headers)

        # Example: Extract the rows
        rows = table.find_all('tr')
        for row in rows:
            cells = row.find_all('td')
            row_data = [cell.text for cell in cells]
            print("Row data:", row_data)
else:
    print("Failed to fetch the webpage.")

"""
# Example: If the tables are contained within a specific div
# div = soup.find('div', id='specific-div-id')
# tables = div.find_all('table')



