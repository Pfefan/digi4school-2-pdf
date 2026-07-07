import os
import re
import tqdm


import requests
from requests.exceptions import HTTPError, RequestException

class BookContentDownloader():
    def __init__(self, session) -> None:
        self.session: requests.Session = session

    def download_svgs(self, down_dir, url, show_progress=False):
        total_pages = None

        file_url, special_book_url = self.get_file_url(url)
        if file_url is None:
            return False

        total_pages = self.get_total_pages(file_url) if show_progress else None
        counter = 1

        # This shows a progress bar for the download if the show_progress
        # parameter is set to True. Otherwise, it just downloads the files.
        with tqdm.tqdm(total=total_pages, desc="Downloading svgs", unit="svg", disable=not show_progress) as pbar:
            while True:
                file_url_with_counter = file_url.format(counter, counter)
                try:
                    response = self.session.get(file_url_with_counter, timeout=5)
                    if response.status_code == 404:
                        if counter == 1:
                            return False
                        break
                    if counter > 1000:
                        break
                    response.raise_for_status()

                except (RequestException, HTTPError):
                    print(f"Error downloading {file_url_with_counter}")
                    return False

                svg_text = response.text

                if special_book_url:
                    svg_text = self.modify_svg_text(svg_text, counter)

                with open(f"{down_dir}/{counter}.svg", "w+", encoding="utf8") as svg_file:
                    svg_file.write(svg_text)

                counter += 1
                pbar.update(1)

        return True

    def download_pages(self, down_dir, url, start_page, end_page, first_non_titlepage, show_progress=False):
        total_page_range = end_page - start_page + 1 if end_page else 1
        end_page = end_page if end_page else start_page

        file_url, special_book_url = self.get_file_url(url)
        if file_url is None:
            return False
            
        counter = start_page + first_non_titlepage - 1
        # This shows a progress bar for the download if the show_progress
        # parameter is set to True. Otherwise, it just downloads the files.
        with tqdm.tqdm(total=total_page_range, desc="Downloading svgs", unit="svg", disable=not show_progress) as pbar:
            while counter <= end_page + first_non_titlepage - 1:
                file_url_with_counter = file_url.format(counter, counter)
                try:
                    response = self.session.get(file_url_with_counter, timeout=5)
                    if response.status_code == 404:
                        if counter == 1:
                            return False
                        break
                    response.raise_for_status()
                except (RequestException, HTTPError):
                    print(f"Error downloading {file_url_with_counter}")
                    return False

                svg_text = response.text
                if special_book_url:
                    svg_text = self.modify_svg_text(svg_text, counter)

                with open(f"{down_dir}/{counter}.svg", "w+", encoding="utf8") as svg_file:
                    svg_file.write(svg_text)

                counter += 1
                pbar.update(1)

        return True


    def download_images(self, svg_dir, url, show_progress=False):
        svg_files = os.listdir(svg_dir)
        total_image = None
        images_urls = []

        for file in svg_files:
            with open(f"{svg_dir}/{file}", "rb") as svg_file:
                svg_contents = svg_file.read().decode('utf-8')

            matches = re.findall(r'<image\s.*?xlink:href="([^"]*)".*?>', svg_contents)

            if matches:
                images_urls.extend(matches)

        total_image = len(images_urls) if show_progress else None

        # This shows a progress bar for the download if the show_progress
        # parameter is set to True. Otherwise, it just downloads the files.
        with tqdm.tqdm(total=total_image, desc="Downloading images", unit="image", disable=not show_progress) as pbar:
            for xlink_href in images_urls:
                image_url = f"{url}/{xlink_href}"
                response = self.session.get(image_url, timeout=5)
                dirname = f"{svg_dir}/{os.path.dirname(xlink_href)}"
                os.makedirs(dirname, exist_ok=True)

                if response.status_code == 200:
                    with open(os.path.join(dirname, os.path.basename(xlink_href)), "wb") as img_file:
                        img_file.write(response.content)
                else:
                    return False

                pbar.update(1)

        return True

    def modify_svg_text(self, svg_text:str, counter):
        pattern = r'<image\s.*?xlink:href="([^"]*)".*?>'
        matches = re.findall(pattern, svg_text)

        if matches:
            for xlink_href in matches:
                new_url = f"{counter}/{xlink_href}"
                svg_text = svg_text.replace(xlink_href, new_url, 1)
        return svg_text

    def get_total_pages(self, url):
        low = 1
        high = 1000
        while low <= high:
            mid = (high + low) // 2
            response = self.session.get(url.format(mid, mid), timeout=5)
            if response.status_code == 404:
                high = mid - 1
            else:
                low = mid + 1
        return high

    def get_file_url(self, url):
        response = self.session.get(f"{url}1.svg", timeout=5)
        if response.status_code != 404:
            return f"{url}{{}}.svg", False
        else:
            response = self.session.get(f"{url}1/1.svg", timeout=5)
            if response.status_code != 404:
                return f"{url}{{}}/{{}}.svg", True
        return None, False
