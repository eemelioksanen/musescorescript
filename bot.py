import requests
import logging
import json
import re
from bs4 import BeautifulSoup


url = "https://musescore.com/user/8927976/scores/1993341"

while(not url):
    url = input('Please enter the url of the music sheet you wish to download: ')
    if ('musescore' not in url):
        print('invalid url address!')
        url = None

# logging.basicConfig(level=logging.DEBUG)

split_url = re.sub('https://', '', url)
split_url = re.sub('www.', '', split_url)
split_url = split_url.split('/')

user_id = split_url[2]
score_id = split_url[4]

header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47"
}

r = requests.get(url, headers=header)

if (r.status_code != 200):
    print("error connecting to {}".format(url))

page = BeautifulSoup(r.content, 'html.parser')

pageregex = re.compile('(pages_count&quot;:[0-9]{1,2})')

pages_count = int(re.findall(
    '[0-9]{1,2}', re.findall(pageregex, r.text)[0])[0])

# exit in case of obscure amount of pages
if (pages_count > 50 or pages_count < 0):
    print("invalid page count (max 50): {}".format(pages_count))
    exit()

regex = re.compile(
    "(https://musescore.com/static/public/build/musescore)(_es6)?(/)[0-9]{1,}(/)[0-9]{1,}(.)[a-z0-9]{1,}(.js)"
)

jmuse = None

for link in page.find_all('link'):
    if (regex.match(link.get('href'))):
        jmuse = link.get('href')
        break

if (not jmuse):
    print("could not find the jmuse link to extract authorization token")
    exit()

r = requests.get(jmuse, headers=header)

if (r.status_code != 200):
    print("error at HTTP GET: {}\nstatus code: {}").__format__(jmuse, r.status_code)

token_regex = re.compile("[a-z0-9]{40}")

token = re.findall(token_regex, r.text)[0]

score_header = {
    "authorization": token,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47"
}

for i in range(0, pages_count):

    print('downloading page {} of {}...'.format(i + 1, pages_count))

    jmuse_url = 'https://musescore.com/api/jmuse?id={}&index={}&type=img&v2=1'.format(
        score_id, i)

    page_url = json.loads(requests.get(jmuse_url, headers=score_header).text)[
                          'info']['url']

    r = requests.get(page_url, headers=header, stream=True)

    if (r.status_code != 200):
        print("an error occured while downloading the files")
        exit()

    with open('./files/score{}.svg'.format(i), 'wb') as svgfile:

        res = requests.get(page_url, headers=header, stream=True)
        for block in res.iter_content():
            if not block:
                break

            svgfile.write(block)
    svgfile.close()