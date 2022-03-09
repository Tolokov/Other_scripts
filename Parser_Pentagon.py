from aiohttp import ClientSession
from aiofiles import open
from asyncio import gather, get_event_loop
from bs4 import BeautifulSoup


async def get_data_page(num_page):
    async with ClientSession() as session:
        url = f'https://www.defense.gov/observe/photo-gallery/igphoto/{num_page}/'

        async with session.get(url) as response:
            if response.status != 200:
                print('--- The page does not exist --- ')
                return None

            content = await response.read()
            soup = BeautifulSoup(content.decode('utf-8'), 'html.parser')
            link_to_photo = soup.find('li', class_='download').a.get('href')

        print(f'Page processed №:{num_page}\tImage address:{link_to_photo}')
        return link_to_photo


async def get_image(path, link_to_photo):
    try:
        if link_to_photo is not None:
            name = link_to_photo.split('/')

            async with ClientSession() as session:
                async with session.get(link_to_photo) as response:
                    content = await response.read()
                    async with open(f'{path}\\{name[-1]}', 'wb') as f:
                        await f.write(content)

            print('Image is save', name[-1])

    except FileNotFoundError as f:
        print('Need to specify a new path')
        exit()

    except OSError as ose:
        # THIS ERROR is triggered, IF YOU USE HDD SLOWLY
        # max speed without OSError it's 50 pages per task (step = 50)
        print(ose)


async def run(start, finish, step, path):
    previous = start - step
    for p in range(start, finish, step):

        try:
            tasks_get_data = []
            t_get_image = []

            for page in range(previous, p):
                task = get_data_page(page)
                tasks_get_data.append(task)

            for link in await gather(*tasks_get_data):
                ta = get_image(path, link)
                t_get_image.append(ta)

            await gather(*t_get_image)

            previous = p

        except BaseException as bas:
            print(f'{bas}')
            with open('log.txt', 'a') as f:
                f.write(f'{bas}\n')
            continue


async def main():
    # url = f'https://www.defense.gov/observe/photo-gallery/igphoto/'
    # first_page = 2_000_000_000
    # path = 'G:\\Parser'

    path = 'your path'

    first_page = 2_000_130_479
    last_page = 2_002_847_499
    step = 10  # optimum:50 max:250

    print(last_page - first_page)  # 2_717_020

    await run(first_page, last_page, step, path)


# 2021/09/05 news: Yandex withstood the largest DDOS attack in the history of Runet
if __name__ == '__main__':
    main_loop = get_event_loop()
    main_loop.run_until_complete(main())

