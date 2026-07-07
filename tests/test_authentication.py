import os

import pytest
import requests
from dotenv import load_dotenv

from src.handlers.authentication import AuthAndTokenHandler
from src.handlers.book_fetcher import BookDataRetriever


class TestLogin:
    @classmethod
    def setup_class(cls):
        load_dotenv()

    def test_login_user_success(self):
        session = requests.Session()
        auth = AuthAndTokenHandler()
        login_status = auth.login_user(session)
        assert login_status is True

    def test_login_user_failure(self):
        session = requests.Session()
        auth = AuthAndTokenHandler()
        original_email = os.environ['EMAIL']
        original_password = os.environ['PASSWORD']
        os.environ['EMAIL'] = "WrongEmail"
        os.environ['PASSWORD'] = "WrongPassword"
        login_status = auth.login_user(session)
        assert login_status is False
        os.environ['EMAIL'] = original_email
        os.environ['PASSWORD'] = original_password

class TestTokenProcessing:
    @classmethod
    def setup_class(cls):
        load_dotenv()

    def test_token_processing(self):
        session = requests.Session()
        auth = AuthAndTokenHandler()
        login_status = auth.login_user(session)
        assert login_status is True

        data = BookDataRetriever().get_book_list(session)[0]
        url = auth.token_processing(data, session)
        assert url == 'https://a.digi4school.at/ebook/' + data[0] + '/'

    def test_token_processing_nested_books(self):
        session = requests.Session()
        auth = AuthAndTokenHandler()
        login_status = auth.login_user(session)
        assert login_status is True

        data = BookDataRetriever().get_book_list(session)
        data = [book for book in data if book[2] == 'English Unlimited HTL 4/5, Schülerbuch mit Audio-CD und CD-ROM und E-Book'][0]
        url = auth.token_processing(data, session)
        assert url == 'https://a.digi4school.at/ebook/' + data[0] + '/1001'
