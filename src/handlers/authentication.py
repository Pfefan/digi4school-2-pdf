"""
This module contains the Authentication class for handling user authentication and token processing 
for accessing the Digi4School platform.
"""
import re
import os

from bs4 import BeautifulSoup

from .config_handler import ConfigHandler


class AuthAndTokenHandler:
    """
    The AuthAndTokenHandler class handles user authentication and token processing
    for accessing the Digi4School platform.
    """

    LOGIN_URL = "https://digi4school.at/br/xhr/login"

    def __init__(self):
        pass

    def get_data(self):
        if os.getenv('EMAIL'):  # Check if it's a test environment
            login_payload = {
                'email': os.getenv('EMAIL'),
                'password': os.getenv('PASSWORD')
            }
        else:
            config_data = ConfigHandler().get_config()
            login_payload = {
                'email': config_data['email'],
                'password': config_data['password']
            }
        return login_payload


    def login_user(self, session):
        """
        Logs in a user using the provided session.

        Args:
            session (Session): The session object used for making HTTP requests.

        Returns:
            bool: A boolean value indicating the login status (True for success, False for failure)
        """
        login_payload = self.get_data()
        response = session.post(self.LOGIN_URL, data=login_payload, timeout=5)

        if str(response.content, 'utf-8') == "OK":
            return True
        elif str(response.content, 'utf-8') == "KO":
            return False

    def token_processing(self, data, session):
        """
        Processes lti request which is needed for authentication.

        Args:
            data (list): The data required for token retrieval.
            session (object): The session object for making HTTP requests.

        Returns:
            redirect_url (str): The URL to the book.
        """
        book_code_url = "https://digi4school.at/ebook/" + data[1]

        book_code_req = session.get(book_code_url)
        book_code_response = book_code_req.content.decode()

        # Proccesses the data from the response to get the action url and
        # the data_payload for the next requests
        action_lti, data_payload = self.process_lti_response(book_code_response)

        # Sends first LTI request for token verification
        first_lti_req = session.post(action_lti, data=data_payload)
        first_lti_response = first_lti_req.content.decode()

        # Proccesses the data from the response to get the action url and
        # the data_payload for the next requests
        action_lti, data_payload = self.process_lti_response(first_lti_response)

        # Sends request to the LTI verification URL to get the final redirect URL
        second_lti_req = session.post(action_lti, data=data_payload, allow_redirects=False)
        redirect_url = second_lti_req.headers["Location"]

        # Sends another request with redirects allowed so the actual html page is loaded
        second_lti_req = session.post(action_lti, data=data_payload, allow_redirects=True)
        second_lti_response = second_lti_req.content.decode()
        soup = BeautifulSoup(second_lti_response, 'html.parser')

        # Checks for nested books and returns if true
        if soup.select_one('#content'):
            id_element = soup.select_one('a[href*="index.html"]')
            if id_element:
                id_value = id_element['href'].split('/')[-2]
                url = redirect_url + id_value
                if not url.endswith('/'):
                    url += '/'
                return url

        return redirect_url

    def process_lti_response(self, response):
        """
        Process the LTI response and extract the payload and the redirect url.

        Args:
            response (str): The LTI response HTML content.

        Returns:
            tuple: A tuple containing the action URL and the payload dictionary.
        """
        data_payload = {}
        for match in re.findall(r"<input name='(\w+)' value='(.*?)'>", response):
            data_payload[match[0]] = match[1]

        action_lti = re.search(r"<form[^>]*action='(.*?)'", response).group(1)
        return action_lti, data_payload
