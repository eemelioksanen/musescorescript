from asyncio.windows_events import NULL
import http
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
logging.basicConfig(level=logging.DEBUG)

split_url = re.sub('https://', '', URL)
split_url = re.sub('www.', '', split_url)
split_url = split_url.split('/')

user = split_url[2]
score = split_url[4]

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

headers2 = {
    "authority": "musescore.com",
    "method": "GET",
    "path": "/ api/jmuse?id = 1993341 & index = 5 & type = img & v2 = 1: scheme: https",
    "accept": "*/*",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "fi, en q = 0.9, en-GB q = 0.8, en-US q = 0.7",
    "authorization": "8c022bdef45341074ce876ae57a48f64b86cdcf5", # important
    "cache-control": "no-cache",
    "pragma": "no-cache",
    "referer": "https: // musescore.com/user/8927976/scores/1993341",
    "sec-ch-ua": "\"Chromium\";v=\"104\", \" Not A;Brand\";v=\"99\", \"Microsoft Edge\";v=\"104\"",
    "sec-ch-ua-mobile": "?0",
    "sec-ch-ua-platform": "\"Windows\"",
    "sec-fetch-dest": "empty",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-orig",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47"
}

r = requests.get(URL, headers=headers)

page = BeautifulSoup(r.content, 'html.parser')

for link in page.find_all('link'):
    print(link.get('href'))

# URL2 = 'https://musescore.com/api/jmuse?id=1993341&index=1&type=img&v2=1'

# URL3 = 'https://musescore.com/api/jmuse?id=4913846&index=1&type=img&v2=1'

# r2 = requests.get(URL2, headers=headers2)

# print(r.text)
# print(r2.json())
