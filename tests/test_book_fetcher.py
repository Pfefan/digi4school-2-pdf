import pytest
from unittest.mock import Mock, patch
from requests import Session
from src.handlers.book_fetcher import BookDataRetriever

class TestGetBooks:
    def test_get_book_list_success(self):
        book_fetcher = BookDataRetriever()
        session = Session()

        session.cookies.set('ad_session_id', 'mock_value')
        session.cookies.set('digi4s', 'mock_value')

        mock_response = Mock()
        mock_response.content = '''
        <div id="shelf">
            <a href='/ebook/10vqygp964ze' target='_blank' data-code='10vqygp964ze' data-id='4215' class='bag'>
                <div>
                    <div class='book_cover'><img src='https://a.digi4school.at/thumb/4215'></div>
                    <div>
                        <h1>Wissen – Können – Handeln Geografie HTL Jg. 1 + E-Book</h1>
                        <h2><span class='publisher'>Ed. Hölzel Gesellschaft m.b.H. Nfg KG</span></h2>
                        <h4>gültig bis 31.10.2026</h4>
                    </div>
                </div>
            </a>
        </div>
        '''

        with patch.object(Session, 'get', return_value=mock_response):
            result = book_fetcher.get_book_list(session)

        assert len(result) == 1
        assert result[0][0] == '4215'
        assert result[0][1] == '10vqygp964ze'
        assert result[0][2] == 'Wissen – Können – Handeln Geografie HTL Jg. 1 + E-Book'
        assert result[0][3] == '/ebook/10vqygp964ze'

    def test_get_book_list_session_not_initialized(self):
        book_fetcher = BookDataRetriever()
        session = None

        with pytest.raises(RuntimeError) as e:
            book_fetcher.get_book_list(session)

        assert str(e.value) == "Session is not initialized or user is not authenticated."

    def test_get_book_list_session_not_authenticated(self):
        book_fetcher = BookDataRetriever()
        session = Session()

        with pytest.raises(RuntimeError) as e:
            book_fetcher.get_book_list(session)

        assert str(e.value) == "Session is not initialized or user is not authenticated."
