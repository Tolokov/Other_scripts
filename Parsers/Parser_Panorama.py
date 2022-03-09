from time import sleep

from bs4 import BeautifulSoup as BS
from requests import get
from pymysql import connect


class Telegram:
    """Publication in telegram channel"""

    def __init__(self, token, text):
        self.api_token = token
        self.my_channel_name = '@NewsPanorama'
        self.panorama_link = 'https://panorama.pub'
        self.text = text

    def send_post(self):
        get(
            'https://api.telegram.org/bot{}/sendMessage'.format(self.api_token),
            params=dict(
                chat_id=self.my_channel_name,
                text=self.panorama_link + self.text
            )
        )


class Parser:
    """Collecting data from the main page of the site and getting all the links"""

    def __init__(self, proxy):
        self.link = 'https://panorama.pub/'
        self.proxy = proxy
        self.page = self.get_page()
        self.content = self.get_soup()
        self.links = self.get_links()

    def get_page(self):
        response = get(self.link, proxies=self.proxy)
        if response.status_code != 200:
            print(response.status_code, 'status_code')
        return response.content

    def get_soup(self):
        soup = BS(self.page, 'html.parser', from_encoding="utf-8")
        return soup

    def get_links(self):
        links = list()
        for link in self.content.find_all('a'):
            href = link.get('href')
            if self.interface_or_news(href):
                links.append(href)
        links = self.delete_duplicate(links)
        return links

    @staticmethod
    def delete_duplicate(links: list) -> tuple:
        return tuple(links)

    @staticmethod
    def interface_or_news(href):
        length = len(href)
        if length < 40 or length > 350:
            return False
        else:
            return True


class History:
    """Saving the history of sent messages to an online database"""

    def __init__(self, server):
        self.server = server
        self.cursor = connect(
            host=self.server['host'],
            user=self.server['user'],
            passwd=self.server['password']
        ).cursor()
        self.content = self.get_text_in_database()

    def get_text_in_database(self):
        query = f"SELECT text FROM {self.server['user']}.Panorama;"
        self.cursor.execute(query)
        result = list()
        for content in self.cursor:
            result.append(content)
        return result

    def set_text_in_database(self, content):
        query = f"INSERT INTO {self.server['user']}.Panorama (text) VALUES ('{content}');"
        self.cursor.execute(query)
        query = "COMMIT;"
        self.cursor.execute(query)

    def __str__(self):
        content = list()
        for text in self.content:
            content.append(text[0])
        return '\n'.join(content)


class Handler:
    """Comparison of the results of the work of Parser and History"""

    def __init__(self, proxy, sql_server, token):
        self.links_from_panorama_website = Parser(proxy).links
        self.obj_history = History(sql_server)
        self.links_from_db = self.obj_history.content
        self.api_token = token

    def run(self):
        ready_for_publication = self.search_in_history(self.links_from_panorama_website, self.links_from_db)
        try:
            for link in ready_for_publication:
                print('prepared for publication: '.format(link))
                self.send(link=link)
                self.obj_history.set_text_in_database(content=link)
                if len(ready_for_publication) > 0:
                    sleep(1133)
        except Exception as exception:
            raise submit_a_bug(self.api_token, exception)
        finally:
            self.obj_history.cursor.close()

    def send(self, link):
        Telegram(token=self.api_token, text=link).send_post()

    @staticmethod
    def search_in_history(content_from_site, content_from_db):
        new_links = (set(content_from_site))
        old_links = (set(i[0] for i in content_from_db))
        links_to_post = new_links - old_links
        return links_to_post


def submit_a_bug(api_token, *args):
    """Error notification"""
    get(
        'https://api.telegram.org/bot{}/sendMessage'.format(api_token),
        params=dict(
            chat_id='@NewsPanoramaException',
            text=f'{args}'
        )
    )


def main(_proxy, _token, _host, _user, _pass):

    proxy = {
        'http': _proxy
    }
    sql_server = {
        'host': _host,
        'user': _user,
        'password': _pass,
    }
    telegram_token = _token

    try:
        Handler(proxy=proxy, sql_server=sql_server, token=telegram_token).run()
        print('Work is done')
    except Exception as exception:
        raise submit_a_bug(telegram_token, exception)


# 2022/02/15 premiere: 'Uncharted'
if __name__ == '__main__':
    _proxy = ''
    _token = ''
    _host = ''
    _user = ''
    _pass = ''
    main(_proxy, _token, _host, _user, _pass)
