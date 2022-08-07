from asyncio.windows_events import NULL
import http
from itertools import dropwhile
from urllib import response
import requests
import logging
import json
from email import header
from types import SimpleNamespace
import re
from bs4 import BeautifulSoup


URL = "https://musescore.com/user/8927976/scores/1993341"

while(not URL):
    URL = input('Please enter the URL of the music sheet you wish to download: ')
    if ('musescore' not in URL):
        print('invalid URL address!')
        URL = None
# logging.basicConfig(level=logging.DEBUG)

split_url = re.sub('https://', '', URL)
split_url = re.sub('www.', '', split_url)
split_url = split_url.split('/')

user_id = split_url[2]
score_id = split_url[4]

headers = {
    "authority": "musescore.com",
    "path": "/user/2072681/scores/2601926",
    "scheme": "https",
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "accept-encoding": "gzip, deflate, br",
    "accept-languages": "i,en;q=0.9,en-GB;q=0.8,en-US;q=0.7",
    "cookie": "cookie: mu_browser_bi=3891983137033902315; mu_browser_uni=V48pNN5S; mu_unregister_user_id=186692941; _pro_abVar4=SCORE_SEARCH_HIGHLIGHT_RESULTS_2021_04_13.B; _ga=GA1.2.161098316.1642877143; _ym_uid=1642877143919465202; _welcome_banner_first_seen_at=1642880743421; learn.tooltip.view.count=6; mscom_new=a279d936cbde005165ccd90e0622c4ac; mu_ab_experiment=1962.1_1977.1_1983.2_2000.1; _mu_dc_regular=%7B%22v%22%3A5%2C%22t%22%3A1659816413%7D; _gid=GA1.2.1051125479.1659816414; _ym_d=1659816414; _ym_isad=1; _csrf=hxqJwnBz3SMlsEKAkODJAaPyPlwqbM6U; mu_has_static_cache=1659877464; _ms_adScoreView=4; _gat=1",
    "dnt": "1",
    "pragma": "no-cache",
    "referer": "https://musescore.com/sheetmusic?text=super%20mario",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "document",
    "sec-fetch-mode": "navigate",
    "sec-fetch-site": "same-origin",
    "sec-fetch-user": "?1",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47"
}

r = requests.get(URL, headers=headers)

page = BeautifulSoup(r.content, 'html.parser')

pageregex = re.compile('(pages_count&quot;:[0-9]{1,2})')

pages_count = int(re.findall(
    '[0-9]{1,2}', re.findall(pageregex, r.text)[0])[0])

if (pages_count > 99):
    exit()

# urlregex1 = re.compile(
# "(https://musescore.com/static/public/build/musescore/)[0-9]{1,}(/)[0-9]{1,}(.)[a-z0-9]{1,}(.js)")

# regex2 = re.compile(
# "(https://musescore.com/static/public/build/musescore_es6/)[0-9]{1,}(/)[0-9]{1,}(.)[a-z0-9]{1,}(.js)")

regex = re.compile(
    "(https://musescore.com/static/public/build/musescore)(_es6)?(/)[0-9]{1,}(/)[0-9]{1,}(.)[a-z0-9]{1,}(.js)"
)

jmuse = None

for link in page.find_all('link'):
    if (regex.match(link.get('href'))):
        jmuse = link.get('href')
        break

print(jmuse)

if (not jmuse):
    print("could not find the jmuse link to extract authorization token")
    exit()

r = requests.get(jmuse, headers=headers)

if (r.status_code != 200):
    print("error at HTTP GET: {}\nstatus code: {}").__format__(jmuse, r.status_code)

token_regex = re.compile("[a-z0-9]{40}")

token = re.findall(token_regex, r.text)[0]

score_header = {
    "authorization": token,
    "referer": "https: // musescore.com/user/{}/scores/{}".format(user_id, score_id),
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47"
}

page_header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47"
}

for i in range(0, pages_count):

    print('downloading page {} of {}...'.format(i + 1, pages_count))

    jmuse_url = 'https://musescore.com/api/jmuse?id={}&index={}&type=img&v2=1'.format(
        score_id, i)

    page_url = json.loads(requests.get(jmuse_url, headers=score_header).text)[
                          'info']['url']

    r = requests.get(page_url, headers=page_header, stream=True)

    if (r.status_code != 200):
        print("an error occured while downloading the files")
        exit()

    with open('score{}.svg'.format(i), 'wb') as svgfile:

        res = requests.get(page_url, headers=page_header, stream=True)
        for block in res.iter_content():
            if not block:
                break

            svgfile.write(block)
    svgfile.close()