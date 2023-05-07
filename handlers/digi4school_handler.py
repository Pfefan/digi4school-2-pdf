import os

import requests
from bs4 import BeautifulSoup as bs
from requests.utils import cookiejar_from_dict

from handlers.config_handler import Config


class Digi4school:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
        })
        self.login_url = "https://digi4school.at/br/xhr/login"
        self.books_list_url = "https://digi4school.at/ebooks"
        self.book_display_url = "https://a.digi4school.at/ebook/"
        self.token_url = "https://a.digi4school.at/lti"

        os.makedirs('download', exist_ok=True)


    def login_user(self):
        payload = {
            'email': 'email',
            'password': 'password'
        }
        data = Config().get_config()
        payload["email"] = data["email"]
        payload["password"] = data["password"]
        response = self.session.post(self.login_url, data=payload, timeout=5)

        if str(response.content, 'utf-8') == "OK":
            return True
        elif str(response.content, 'utf-8') == "KO":
            return False

    def get_page(self):
        books = []
        if self.session is None:
            raise ValueError("Session is not initialized.")

        response = self.session.get(self.books_list_url, timeout=5)

        soup = bs(response.content, 'html.parser')

        shelf_div = soup.find('div', {'id': 'shelf'})

        a_tags = shelf_div.find_all('a')

        for a_tag in a_tags:
            href = a_tag.get('href')

            data_id = a_tag['data-id']
            data_code = a_tag['data-code']
            h1_text = a_tag.find('h1').text
            books.append((data_id, data_code, h1_text, href))

        return books

    def get_token(self, data):
        # right now firstly the list-files has to be executed to get the cookies, i will change that in the future i am just
        # trying to implement the feature right now, the request with the id needs the digi4s cookie from the home page
        book_code_url = "https://digi4school.at/ebook/" + data[1]
        lti_url = "https://a.digi4school.at/lti"

        cookies = self.session.cookies.get_dict()

        book_code_req = self.session.get(book_code_url)
        print(book_code_req.content)
        book_code_cookies = book_code_req.cookies.get_dict()

        headers = {
            'Host': 'a.digi4school.at',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/113.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://kat.digi4school.at/',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Content-Length': '474',
            'Origin': 'https://kat.digi4school.at',
            'Connection': 'keep-alive',
            'Cookie': f'digi4s={book_code_cookies["digi4s"]}',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'same-site'
        }
        print(book_code_cookies["digi4s"])
        # this request takes the cookie from the book id request to get a new session_id token
        first_lti_req = self.session.get(lti_url, headers=headers)
        print(first_lti_req.status_code)
        print(self.session.cookies.get_dict())
        
        print(first_lti_req.cookies.get_dict())

    def download_book(self, data):
        url = self.book_display_url + data[0]
        down_dir = f'download/{data[0]}'
        
        self.get_token(data)

        self.session.get(url, timeout=5)
        if 1 == 3:
            cookies = self.session.cookies.get_dict()
            digi4b = "2299266513%2c7553%2c22s5bzuagyky%2c252212%20{982%201681475730%20B895BAA86447BB34B758579E37D1E600BB67619A}"

            headers = {
                'Cookie': 'digi4b="{digi4b}"; ad_session_id={ad_session_id}; digi4s={digi4s}'.format(digi4b=digi4b, ad_session_id=cookies["ad_session_id"], digi4s=cookies["digi4s"]),
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'
            }

            counter = 1

            os.makedirs(down_dir)


            while True:
                file_url = f"{url}/{counter}.svg"
                response = self.session.get(file_url, headers=headers, timeout=10)

                if response.status_code == 404:
                    break

                with open(f"{down_dir}/{counter}.svg", "w+", encoding="utf8") as f:
                    f.write(response.text)

                counter += 1

        #print(f"All SVG files for book {book_id} have been downloaded to {down_dir}.")
