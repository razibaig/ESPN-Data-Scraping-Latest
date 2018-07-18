import scrapy
from bs4 import BeautifulSoup as B
from parsel import Selector
import json
import urllib.request
import time
import scrapy
from scrapy.selector import Selector
import requests


URLS = []


class QuotesSpider(scrapy.Spider):
    name = "quotes"
    start_urls = [
        'http://www.espncricinfo.com/england/content/player/351588.html',
    ]
    INDEX = 0
    DATA_LIST = {}

    def parse(self, response):
        p_info = []
        l_articles = []
        l_photos = []

        file = open("player.html", "w")
        file.write(response.text)
        file.close()

        response = Selector(response.text)
        test_header2 = response.css("p.ciPlayerinformationtxt").extract()
        pl = B(''.join(test_header2), 'html.parser')
        head = pl.find_all('p')

        i = 0
        personal_info = {}
        for tag in head:
            t = head.__getitem__(i)
            key = t.contents[0].string
            info = []
            for j in range(2, len(t.contents)):
                if t.contents[j].string != ' ':
                    info.append(t.contents[j].string)
            personal_info[key] = info
            i += 1

        # player.personal_info['Personal Information'] = personal_info

        ind = 0
        all_tables = response.css("table.engineTable").extract()
        for table in all_tables:
            (self.print_table(table, "engineTable"))
            ind += 1

        player_table_s = response.css("div#shrtPrfl").extract_first()
        if player_table_s:
            player_prof_s = B(''.join(player_table_s), 'html.parser')
            for tag in player_prof_s.find_all('p'):
                p_info.append(tag.string)

        player_table = response.css("div#plrpfl").extract()
        if player_table:
            player_prof = B(''.join(player_table), 'html.parser')
            for tag in player_prof.find_all('p'):
                p_info.append(tag.string)

        articles = response.css("div.headline").extract_first()
        soup = B(''.join(articles), 'html.parser')
        for a in soup.find_all('a', href=True):
            l_articles.append("http://www.espncricinfo.com" + a['href'])

        photos = response.css("div.ciPicHldr").extract()
        soup = B(''.join(photos), 'html.parser')
        for a in soup.find_all('a', href=True):
            l_photos.append(soup.img['src'])

        player = Player(personal_info, self.DATA_LIST[0], self.DATA_LIST[1], self.DATA_LIST[3],
                        p_info, l_articles, l_photos)

        s = json.dumps(player.__dict__, indent=4, sort_keys=True)

        print(s)

        with open('player.json', "w") as file:
            file.write(s)

    def print_table(self, table, class_name):

        soup = B(''.join(table), "html.parser")
        table = soup.find("table", attrs={"class": class_name})

        # The first tr contains the field names.
        headings = [th.get_text() for th in table.find("tr").find_all("th")]

        datasets = []
        for row in table.find_all("tr")[1:]:
            dataset = zip(headings, (td.get_text() for td in row.find_all("td")))
            datasets.append(dataset)

        tuple_list = []
        for dataset in datasets:
            tuple = {}
            for field in dataset:
                tuple[field[0].strip()] = field[1].strip()
            tuple_list.append(tuple)

        self.DATA_LIST[self.INDEX] = tuple_list
        self.INDEX += 1


class Player:
    def __init__(self, info, bat_avg, bowl_avg, recent_mat, player_info, articles, photos):

        self.personal_info = info
        self.batting_averages = bat_avg
        self.bowling_averages = bowl_avg
        self.recent_matches = recent_mat
        self.profile_info = player_info
        self.latest_articles = articles
        self.latest_photos = photos

    def print_player(self):
        print(self.personal_info)
        print(self.batting_averages)
        print(self.bowling_averages)
        print(self.recent_matches)
        print(self.profile_info)
        print(self.latest_articles)
        print(self.latest_photos)


# Retrieve a single page and report the URL and contents
def load_url(url, timeout):
    time.sleep(0.5)
    with urllib.request.urlopen(url, timeout=timeout) as conn:
        return conn.read()


# Filter the links found in <a> tags
def filter_links(all_links):
    cleaned_links = []
    for i in range(len(all_links)):
        if "/content/player/" in all_links[i]:
            cleaned_links.append(all_links[i])
    return cleaned_links


# Populate the complete urls
def populate_urls(prefix_string, cleaned_links):
    for i in range(len(cleaned_links)):
        complete_url = prefix_string + cleaned_links[i]
        URLS.append(complete_url)


def main():
    source_page = 'http://www.espncricinfo.com/england/content/player/caps.html?'
    espn_url = 'http://www.espncricinfo.com'

    country = 1
    m_type = 1
    scrap_url = "{0}{1}{2}{3}{4}{5}".format(source_page, "country=", country, ";", "class=", m_type)
    print(scrap_url)

    f = urllib.request.urlopen(scrap_url)
    complete_html = f.read()
    # print(complete_html)

    all_found_links = Selector(text=complete_html).xpath('.//a/@href').extract()

    filtered_links = filter_links(all_found_links)

    print(len(list(filtered_links)))

    populate_urls(espn_url, filtered_links)


if __name__ == "__main__":
    main()
