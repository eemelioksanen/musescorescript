from ntpath import join
import requests
import json
import re
from bs4 import BeautifulSoup
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
from io import BytesIO
from PIL import Image
from os import rename, path, getcwd, makedirs
import sys

# variables
# set a folder where the pdf and images are downloaded, leaving this empty will download the content directly to working directory
output_folder = ""
# default name for the pdf in case the title is invalid or such a file exists already
default_output_name = "output_default.pdf"

save_images = False
url = None

if (len(sys.argv) < 2):
    print("invalid number of arguments!")
    exit()

for i in range(1, len(sys.argv) - 1):
    match sys.argv[i]:
        case "-m":
            save_images = True
        case _:
            print("unknown argument!")
            exit()

url = sys.argv[len(sys.argv) - 1]

if (not url):
    print("please enter a valid url!")

split_url = re.sub('https://', '', url)
split_url = re.sub('www.', '', split_url)
split_url = split_url.split('/')

score_id = None

if (len(split_url) == 5):
    score_id = split_url[4]

else:
    score_id = split_url.pop()

header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47"
}

r = requests.get(url, headers=header)

if (r.status_code != 200):
    print("error connecting to {}".format(url))

page = BeautifulSoup(r.content, "html.parser")

title = page.title.text.replace(" | Musescore.com", "")

print(title)

pageregex = re.compile("(pages_count&quot;:[0-9]{1,2})")

pages_count = int(re.findall(
    "[0-9]{1,2}", re.findall(pageregex, r.text)[0])[0])

print("pages: {}".format(pages_count))

# exit in case of obscure amount of pages
if (pages_count > 50 or pages_count < 0):
    print("invalid page count (max 50): {}".format(pages_count))
    exit()

regex = re.compile(
    "(https://musescore.com/static/public/build/musescore)(_es6)?(/)[0-9]{1,}(/)[0-9]{1,}(.)[a-z0-9]{1,}(.js)"
)

jmuse = None

for link in page.find_all("link"):
    if (regex.match(link.get("href"))):
        jmuse = link.get("href")
        break

if (not jmuse):
    print("could not find the jmuse link to extract authorization token")
    exit()

r = requests.get(jmuse, headers=header)

if (r.status_code != 200):
    print("error at HTTP GET: {}\nstatus code: {}").__format__(
        jmuse, r.status_code)

token_regex = re.compile("[a-z0-9]{40}")

token = re.findall(token_regex, r.text)[0]

score_header = {
    "authorization": token,
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47"
}

filetype = requests.get(
    json.loads(
        requests.get(f"https://musescore.com/api/jmuse?id={score_id}&index=0&type=img&v2=1",
                     headers=score_header).text)
    ['info']['url']).headers['Content-Type']

print("image content type: {}".format(filetype))

filepath = path.join(getcwd(), output_folder)

makedirs(filepath, exist_ok=True)

filepath = path.join(filepath, default_output_name)

image_output_folder = path.join(
    getcwd(), output_folder, score_id + "_images", "")


def download_image(index):  # downloads an image and returns a BytesIO-filelike object
    print("downloading image {} of {}...".format(
        index + 1, pages_count))
    jmuse_url = "https://musescore.com/api/jmuse?id={}&index={}&type=img&v2=1".format(
        score_id, i)
    page_url = json.loads(requests.get(jmuse_url, headers=score_header).text)[
        "info"]["url"]
    res = requests.get(page_url, headers=header)
    if (res.status_code != 200):
        print("an error occured while downloading the files")
        exit()

    file = BytesIO(res.content)
    return file


if (save_images):
    makedirs(image_output_folder, exist_ok=True)


if (filetype == "image/svg+xml"):

    c = canvas.Canvas(filepath)

    for i in range(0, pages_count):

        svgfile = download_image(i)

        if (save_images):
            file = open(path.join(image_output_folder,
                        "score{}.svg".format(i)), "wb")
            file.write(svgfile.getbuffer())
            file.close()

        drawing = svg2rlg(svgfile)

        scale = 595.0 / drawing.width

        drawing.scale(scale, scale)

        renderPDF.draw(drawing, c, 0, 0, 0)

        c.showPage()

    print("generating pdf...")
    c.save()

elif (filetype == "image/png"):

    images = []

    for i in range(0, pages_count):

        pngfile = download_image(i)

        image = Image.open(pngfile)

        if (save_images):
            file = open(path.join(image_output_folder,
                        "score{}.png".format(i)), "wb")
            file.write(pngfile.getbuffer())
            file.close()

        images.append(image)

    print("generating pdf...")
    images[0].save(filepath, "PDF", resolution=100.0,
                   save_all=True, append_images=images[1:])

else:
    print("unknown file type: {}\nhalting...".format(filetype))
    exit()

try:
    new_name = re.sub(re.compile("[^0-9a-zA-Z,()' ]"), "", title)
    new_name += ".pdf"
    rename_path = path.join(getcwd(), output_folder, new_name)
    rename(filepath, rename_path)
    print("pdf successfully saved to {}".format(rename_path))

except:
    print("renaming the pdf file failed, saved using default name: \"{}\"\nperhaps the file already exists?".format(filepath))

if (save_images):
    print("images saved: {}".format(image_output_folder))
