import requests
from bs4 import BeautifulSoup, NavigableString
from icecream import ic

class Parser:
    def __init__(self):
        '''
        self.response = requests.get('https://www.warframe.com/zh-hant/droptables')ad
        self.status = self.response.status_code
        self.content = self.response.text
        '''
        self.soup = self.get_soup()
        self.update_date = self.soup.find('p').text.split(':')[-1].strip()
        for child in self.soup.html.body:
            if not isinstance(child, NavigableString):
                print(child.string)

    @staticmethod
    def get_soup():
        with open(r'C:\Users\jethr\PycharmProjects\Warframe\Warframe PC Drops.html', mode='r', encoding='utf-8') as fp:
            return BeautifulSoup(fp, 'html.parser')



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



