from asyncio import as_completed
from ntpath import join
import requests
import json
import re
from bs4 import BeautifulSoup
from io import BytesIO
from os import rename, path, getcwd, makedirs
import sys
from svglib.svglib import svg2rlg
import concurrent.futures
from reportlab.graphics import renderPDF
from reportlab.pdfgen import canvas
import img2pdf


def main():
    # variables
    # set a folder where the pdf and images are downloaded, leaving this empty will download the content directly to working directory
    output_folder = ""
    # default name for the pdf in case the title is invalid or such a file exists already
    default_output_name = "output_default.pdf"
    max_pages = 150

    save_images = False
    url = None

    if len(sys.argv) < 2:
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

    if "musescore.com/" not in url:
        print("please enter a valid url!")
        exit()

    split_url = re.sub("https://", "", url)
    split_url = re.sub("www.", "", split_url)
    split_url = split_url.split("/")

    score_id = None

    if len(split_url) == 5:
        score_id = split_url[4]

    else:
        score_id = split_url.pop()

    header = {
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47"
    }

    r = requests.get(url, headers=header)

    if r.status_code != 200:
        print(f"error connecting to {url}")

    page = BeautifulSoup(r.content, "html.parser")

    title = page.title.text.replace(" | Musescore.com", "")

    print(title)

    pageregex = re.compile("(pages_count&quot;:[0-9]{1,3})")

    pages_count = int(re.findall("[0-9]{1,3}", re.findall(pageregex, r.text)[0])[0])

    print(f"pages: {pages_count}")

    # exit in case of obscure amount of pages
    if pages_count > max_pages or pages_count < 0:
        print(f"invalid page count (max {max_pages}): {pages_count}")
        exit()

    token = "8c022bdef45341074ce876ae57a48f64b86cdcf5"  # hard coded auth token

    score_header = {
        "authorization": token,
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.5112.81 Safari/537.36 Edg/104.0.1293.47",
    }

    filetype = requests.get(
        json.loads(
            requests.get(
                f"https://musescore.com/api/jmuse?id={score_id}&index=0&type=img&v2=1",
                headers=score_header,
            ).text
        )["info"]["url"]
    ).headers["Content-Type"]

    print(f"image content type: {filetype}")

    filepath = path.join(getcwd(), output_folder)

    makedirs(filepath, exist_ok=True)

    filepath = path.join(filepath, default_output_name)

    image_output_folder = path.join(getcwd(), output_folder, score_id + "_images", "")

    def download_image(
        index,
    ):  # downloads an image and returns a BytesIO-filelike object
        jmuse_url = (
            f"https://musescore.com/api/jmuse?id={score_id}&index={index}&type=img&v2=1"
        )
        page_url = json.loads(requests.get(jmuse_url, headers=score_header).text)[
            "info"
        ]["url"]
        res = requests.get(page_url, headers=header)
        if res.status_code != 200:
            print("an error occured while downloading the files")
            exit()

        file = BytesIO(res.content)
        return (index, file)

    def download_all():  # downloads all images from index 0 to pages_count - 1
        images = [None] * pages_count
        print("downloading images...")
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future_img = {
                executor.submit(download_image, i): i for i in range(0, pages_count)
            }
            for future in concurrent.futures.as_completed(future_img):
                images[future.result()[0]] = future.result()[1]

        return images

    def write_images(images, extension):
        for i in range(0, pages_count):
            f = open(path.join(image_output_folder, f"score{i}.{extension}"), "wb")
            f.write(images[i].getbuffer())
            f.close()

    def draw_all_svg(images):

        drawing_progress = "[" + pages_count * "." + "]"

        def draw(img):
            svg = svg2rlg(img)
            scale = 595.0 / svg.width
            svg.scale(scale, scale)
            return svg

        drawn_images = []

        for img in images:
            drawn_images.append(draw(img))

            drawing_progress = drawing_progress.replace(".", "#", 1)
            print(drawing_progress, end="\r")
        print("")
        return drawn_images

    if save_images:
        makedirs(image_output_folder, exist_ok=True)

    if filetype == "image/svg+xml":

        c = canvas.Canvas(filepath)

        images = download_all()

        pdf_progress = "[" + pages_count * "." + "]"

        if save_images:
            write_images(images, "svg")

        print("drawing images...")
        svg_images = draw_all_svg(images)

        print("generating pdf file...")

        for img in svg_images:

            renderPDF.draw(img, c, 0, 0, 0)

            c.showPage()

            pdf_progress = pdf_progress.replace(".", "#", 1)

            print(pdf_progress, end="\r")

        c.save()
        print("")
        print("")

    elif filetype == "image/png":

        images = download_all()

        if save_images:
            write_images(images, "png")

        print("generating pdf...")

        a4inpt = (img2pdf.mm_to_pt(310), img2pdf.mm_to_pt(297))
        layout_fun = img2pdf.get_layout_fun(a4inpt)
        with open(filepath, "wb") as f:
            f.write(img2pdf.convert(images, layout_fun=layout_fun))

    else:
        print(f"unknown file type: {filetype}\nhalting...")
        exit()

    try:
        new_name = re.sub(re.compile("[^0-9a-zA-Z,()' ]"), "", title)
        new_name += ".pdf"
        rename_path = path.join(getcwd(), output_folder, new_name)
        rename(filepath, rename_path)
        print(f"pdf successfully saved to {rename_path}")

    except:
        print(
            f'renaming the pdf file failed, saved using default name: "{filepath}"\nperhaps the file already exists?'
        )

    if save_images:
        print(f"images saved to: {image_output_folder}")


if __name__ == "__main__":
    main()
