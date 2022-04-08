from re import findall, search
from datetime import datetime

import lxml
from requests import get, session
from bs4 import BeautifulSoup


class Session:
    """
    Get content from the page
    """

    def __init__(self):
        super().__init__()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'ru',
            'Accept-encoding': 'gzip, deflate, br',
            'Accept-language': 'ru,en;q=0.9',
            'X-requested-with': 'XMLHttpRequest',
            'Upgrade-Insecure-Requests': '1',
            'Sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Yandex";v="21"',
        }
        self.session = session()
        self.session.headers = self.headers

    def get_content(self, urls):
        web_content = list()
        for url in urls:
            response = get(url)
            if response.status_code != 200:
                print(response.status_code, 'status_code', url)
                continue
            soup = BeautifulSoup(response.content, 'lxml', from_encoding="utf-8")
            web_content.append(soup)
        return web_content


class Sites:
    """
    Receiving all posts
    """

    def __init__(self, all_sites):
        super().__init__()
        self.all_sites = all_sites
        self.websites = list()
        self.final_content = list()
        self.count_posts = 0

        for name_site in self.all_sites:
            if name_site[0]:
                self.websites.append(name_site[1])

    def counter(self):
        self.count_posts += 1

    def price_decomposition(self, price):
        numbs = findall(r'\d+', price)
        if len(numbs) == 1:
            return int(numbs[0])
        elif len(numbs) == 2:
            return int(numbs[0] + numbs[1])
        else:
            return '~'

    def scrap_fl(self, soup, time):

        pattern_price = r'[^(a> )]+.(?=&nbsp;<span)'
        pattern_description = r'[^(">)]+(?= <)'
        pattern_how_many_answers = r'[^(span>&nbsp;&nbsp;)]+(?=&n)'
        pattern_how_long = r'[^(.span>)]+(?=<.a>)'

        for post in soup.select('div.b-post__grid'):

            if '' in post.text:
                script = post.find_all('script')

                title = post.a.text.replace('', '')
            else:
                script = post.find_all('script')
                title = post.a.text

            description = search(pattern_description, script[1].text)
            if description is not None:
                description = description.group(0)[1:200].replace('&nbsp;', '').replace('\u20bd', '')
            else:
                description = ''

            link = post.find('a').get('href')

            if 'По договоренности' in script[0].string:
                price = '~'
            else:
                price = search(pattern_price, script[0].string)
                if price is not None:
                    price = price.group(0).replace('&nbsp;', '')
                else:
                    price = '~'

            how_long = search(pattern_how_many_answers, script[2].text).group(0)[1:]

            timer = how_long.split()
            if len(timer) == 5:
                timer = int(timer[0]) * 60 + int(timer[2])
            elif len(timer) == 3:
                timer = int(timer[0])
            else:
                if 'что' in timer:
                    timer = 2
                else:  # Вакансия
                    timer = 400

            if timer > time:
                continue
            self.counter()

            how_many_answers = search(pattern_how_long, script[2].text).group(0)
            if '25' in how_many_answers:
                how_many_answers = 25
            elif '10' in how_many_answers:
                how_many_answers = 10
            elif '5':
                how_many_answers = 5
            else:
                how_many_answers = 0

            link = 'https://www.fl.ru' + link

            self.final_content.append((timer, title[:70], description[:100], price, how_many_answers, link))

    def scrap_freelancehunt(self, soup, time):
        for post in soup.find_all('tr'):
            title = post.find('a').text

            price = post.find('div', class_='text-green')
            if price is not None:
                price = post.div.text[:-2].replace('\n', '')
            else:
                price = '~'

            description = post.find('a')['title'].replace('\n', '')

            how_long = post.select('td.text-center.hidden-xs')[1].div['title']

            timer = how_long.split()
            if len(timer) == 4:
                timer = int(timer[1]) * 60 * 24
            elif len(timer) == 6:
                if 'день' in timer or 'дня' in timer:
                    timer = int(timer[1]) * 24 * 60 + int(timer[3]) * 60
                elif 'часа' in timer or 'часов' in timer or 'час' in timer:
                    timer = int(timer[1]) * 60 + int(timer[3])
            else:
                timer = 1

            if timer > time:
                continue
            self.counter()

            how_many_answers = post.select('div.hidden-xs')

            if not how_many_answers:
                how_many_answers = 0
            else:
                how_many_answers = how_many_answers[0].small.text.replace('\n', '')
                how_many_answers = how_many_answers[0:2].replace(' ', '')

            link = post.find('a').get('href')

            self.final_content.append((timer, title[:70], description[:100], price, how_many_answers, link))

    def scrap_freelancejob(self, soup, time):

        now = datetime.now()
        pattern_date = r'[0-9]+.[0-9]+.[0-9]{4} в [0-9][0-9]:[0-9][0-9]'

        for post in soup.find_all('div', class_='x17'):

            title = post.div.a.text

            price = post.find('div', class_='x18').text
            if 'по' in price:
                price = '~'
            else:
                price = self.price_decomposition(price)

            description = list(post.div.next_siblings)[1].text[:200].replace('\n', '')

            how_many_answers = 'Ответов: ' + post.find('div', class_='x20').text
            how_many_answers = how_many_answers[-2:].replace(' ', '')

            how_long = post.find('div', class_='x20').text
            how_long = search(pattern_date, how_long).group(0).replace('	', '')

            link = post.find('a').get('href')
            link = 'https://www.freelancejob.ru' + link

            timer = how_long.split()
            day, month, year = timer[0].split('.')
            hour, minute = timer[2].split(':')
            day = now.day - int(day)
            month = now.month - int(month)
            hour = now.hour - int(hour)
            minute = now.minute - int(minute)
            timer = sum([day * 60 * 24, month * 60 * 24 * 30, hour * 60, minute])

            if timer > time:
                continue
            self.counter()

            self.final_content.append((timer, title[:70], description[:100], price, how_many_answers, link))

    def scrap_habr(self, soup, time):
        for post in soup.find_all('li', class_='content-list__item'):

            title = post.article.find('a').text

            price = post.find('span', class_='count')
            if price is None:
                price = '~'
            else:
                price = self.price_decomposition(str(price))

            description = ''

            if post.find('i', class_='params__count') == None:
                how_many_answers = 0
            else:
                how_many_answers = post.find('i', class_='params__count').text
            how_long = post.select('span.params__published-at.icon_task_publish_at')[0].span.text

            timer = how_long.split()

            if len(timer) == 3:
                if 'дней' in timer or 'день' in timer:
                    timer = int(timer[0]) * 24 * 60
                else:
                    timer = int(timer[0])
            elif len(timer) == 4:
                timer = int(timer[1]) * 60

            if timer > time:
                continue
            self.counter()

            link = post.article.find('a').get('href')
            link = 'https://freelance.habr.com' + link

            self.final_content.append((timer, title[:70], description[:100], price, how_many_answers, link))

    def scrap_freelance(self, soup, time):

        now = datetime.now()

        for post in soup.find_all('div', class_='box-shadow'):

            title = post.find('a').text
            title = findall(r'[а-яА-Я]+', title)
            if len(title) == 1:
                return title[0]
            elif len(title) > 1:
                answer = str()
                for i in title:
                    answer = answer + ' ' + i
                title = answer[1:]

            description = post.find_all('a')[1].text[1:150].replace('\n', '').replace('\r', '')
            for i in ['  ', '\n\n']:
                description = description.replace(i, '')

            price = post.find('div', class_="cost").text.replace('  ', '').replace('\n', '')
            if 'Договорная' in price:
                price = '~'
            else:
                price = self.price_decomposition(price)

            how_long = post.find('span', class_="prop")['title'][12:]

            how_many_answers = post.find_all('span', class_="prop")[-1].text[2:].replace('  ', '')[-2:].replace(' ', '')

            link = 'https://freelance.ru' + post.find('a').get('href').replace('\n', '')
            link = link.replace('\n', '')

            timer = how_long.split()

            year, month, day = timer[0].split('-')
            hour, minute = timer[2].split(':')

            day = now.day - int(day)
            month = now.month - int(month)
            hour = now.hour - int(hour)
            minute = now.minute - int(minute)
            timer = sum([day * 60 * 24, month * 60 * 24 * 30, hour * 60, minute])

            if len(title) + len(description) < 5 or timer > time:
                continue
            self.counter()

            self.final_content.append((timer, title[:70], description[:100], price, how_many_answers, link))

    def scrap_weblancer(self, soup, time):
        for post in soup.find_all('div', class_='click_container-link')[5:]:

            title = post.find('a').text

            link = 'https://www.weblancer.net' + post.find('a').get('href')

            description = ''

            how_many_answers = post.select('div.float-left.float-sm-none.text_field')[0].text.replace('\n', '').replace(
                '\t', '')
            if 'нет' in how_many_answers:
                how_many_answers = 0
            else:
                how_many_answers = self.price_decomposition(how_many_answers)

            price = post.find('div', class_='indent-xs-b0').span
            if price == None:
                price = '~'
            else:
                price = price.text.replace('$', '')
                # currency = ''

            how_long = post.select('div.col-sm-4.text-sm-right')[0].text

            timer = how_long.split()
            if 'часов' in timer or 'час' in timer:
                timer = int(timer[0]) * 60
            elif 'день' in timer or 'дня' in timer or 'дней' in timer:
                timer = int(timer[0]) * 60 * 24
            else:
                timer = int(timer[0])

            if timer > time:
                continue
            self.counter()

            self.final_content.append((timer, title[:70], description[:100], price, how_many_answers, link))


class Scraper(Sites, Session):
    """
    Gets a list of sites, parses it, outputs the result to the console
    """

    def __init__(self, *args):
        super().__init__(*args)

    def _print_content(self, soups):
        for soup in soups:
            print(f'{soup.title.text}')

    def read(self, all_works):
        all_works.sort(key=lambda x: x[0])
        for post in reversed(all_works):
            print(
                f'-' * 23,
                f'\n{post[1]}\n{post[2]}\n'
                # f'оплата: {post[3]}\t ответов:{post[4]}\n'
                f'{post[5]}'
            )

    def scrapper(self, soups, time):
        """place for error"""
        for soup in soups:
            match soup.title.text[:25]:
                case '⭐Удаленная работа для про' | 'fl.ru':
                    self.scrap_fl(soup, time)
                case 'Работа по парсингу данных' | 'freelancehunt.com':
                    self.scrap_freelancehunt(soup, time)
                case 'Работа, заказы, предложен' | 'freelancejob.ru':
                    self.scrap_freelancejob(soup, time)
                case 'Заказы — Хабр Фриланс' | 'habr':
                    self.scrap_habr(soup, time)
                case 'Фильтр заданий - Проекты ' | 'freelance.ru':
                    self.scrap_freelance(soup, time)
                case 'Веб-программирование: зак' | 'Страница 2: Веб-программи' | 'weblancer.net':
                    self.scrap_weblancer(soup, time)
                case _:
                    raise NameError

    def __repr__(self):
        return f'\nСобрано постов:{self.count_posts}'

    def run(self, time=10000):
        web_content = self.get_content(self.websites)
        self.scrapper(web_content, time)
        self.read(self.final_content)
        self.final_content.clear()


def main():
    # column selection mode
    sites = (
        (True, 'https://freelance.habr.com/tasks'),
        (True, 'https://www.weblancer.net/jobs/veb-programmirovanie-31/'),
        (True, 'https://www.weblancer.net/jobs/veb-programmirovanie-31/?page=2'),

        # These sites stopped working in mid-March, need update
        # (False, 'https://www.fl.ru/projects/category/programmirovanie/'),
        # (False, 'https://freelancehunt.com/projects/skill/parsin-dannyih/169.html'),
        # (False, 'https://www.freelancejob.ru/projects/'),
        # (False, 'https://freelance.ru/project/search/pro?c=&q=парсинг&m=&e=&f=&t=&o=0&o=1'),
    )

    Work = Scraper(sites)
    time = 200  # minute
    Work.run(time)
    print(Work)


# 2021/09/24 news: Global Climate Strike
if __name__ == "__main__":
    main()
