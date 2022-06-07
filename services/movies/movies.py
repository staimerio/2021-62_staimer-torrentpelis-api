"""Services for novels controller"""

# Retic
from retic import env, App as app

# Requests
import requests

# Time
from time import sleep

# bs4
from bs4 import BeautifulSoup

import base64

# Services
from retic.services.responses import success_response, error_response
from services.utils.general import get_node_item
from retic.services.general.urls import slugify

# Models
# from models import Hentai, HentaiPost, Chapter, Image

# Constants
HEADERS = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'accept-encoding': 'gzip, deflate, br',
    'accept-language': 'es-ES,es;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'cookie': '_ga=GA1.2.299160289.1639853243; _gid=GA1.2.1479136229.1640791229; ufp2=12b3ac71463e006d121d5fc1a9e2aa9839754c0f',
    'pragma': 'no-cache',
    'referer': 'https://www.cinecalidad.lat/',
    'sec-ch-ua': '" Not A;Brand";v="99", "Chromium";v="96", "Google Chrome";v="96"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36'
}
DEFAULT_SIZE_MOVIES_HD = app.config.get("DEFAULT_SIZE_MOVIES_HD")
DEFAULT_SIZE_MOVIES_4K = app.config.get("DEFAULT_SIZE_MOVIES_4K")


class Torrentpelis(object):

    def __init__(self):
        """Set the variables"""
        self.year = app.config.get("TORRENTPELIS_YEAR")
        self.url_base = app.config.get("TORRENTPELIS_URL_API_BASE")
        self.site = app.config.get("TORRENTPELIS_SITE")
        self.host = app.config.get("TORRENTPELIS_HOST")
        self.langname = app.config.get("TORRENTPELIS_LANGNAME")

    def get_movie_info(self, id):
        mirrors = list()
        service = "uTorrent"
        r_download_page = requests.get("{0}?p={1}".format(self.url_base, id))
        _soup = BeautifulSoup(r_download_page.content, 'html.parser')
        mirrors = self.get_data_video(_soup, service)
        """Get info about the item"""
        _info = self.get_data_post(_soup)
        if not _info:
            """Return error if data is invalid"""
            return error_response(
                msg="Item not found."
            )
        """Set the data response"""
        _data_response = {
            'mirrors': mirrors,
            **_info
        }
        return success_response(
            data=_data_response
        )

    def get_data(self, page, service):
        _urls = []
        _mirrors = []

        _rows = page.find_all("tr")
        if(len(_rows) < 2):
            return None
        _rows.pop(0)

        for _item in _rows:
            _mirrors.append(self.get_url_torrent(_item, service))
        return _mirrors

    def get_data_video(self, _soup, service):
        _panel_descarga = _soup.find(class_="links_table")

        if not _panel_descarga:
            return None
        return self.get_data(_panel_descarga, service)

    def get_url_torrent(self, item, service):

        _url_torrent = item.find("a", href=True)['href']
        _url_torrent = base64.b64decode(
            _url_torrent.split('urlb64=')[-1]).decode('utf-8')
        r_download_page = None
        try:
            r_download_page = requests.get(_url_torrent)
            _soup = BeautifulSoup(r_download_page.content, 'html.parser')
            _url = _soup.find(id="link", href=True)['href']
        except Exception as err:
            _url = err.args[0].split(
                "No connection adapters were found for '")[-1].split("'")[0]

        _title = ""

        _columns = item.find_all("td")

        _quality = _columns[1].text
        _lang = _columns[2].text
        _size = _columns[3].text
        return {
            u'server': service,
            u'url': _url,
            u'title': _title,
            u'quality': _quality,
            u'lang': _lang,
            u'size': _size,
        }

    def get_data_post(self, _soup):
        _single = _soup.find(class_="poster")
        _img = _single.find('img')['data-src']
        _title = _soup.find("h1").text

        return {
            'title': _title,
            'img': _img
        }


def get_instance():
    """Get an MTLNovel instance from a language"""
    return Torrentpelis()


def get_data_items_raw(instance, page=0):
    """GET Request to url"""
    _url = "{0}/peliculas/page/{1}".format(instance.url_base, page)
    _req = requests.get(_url)
    """Format the response"""
    _soup = BeautifulSoup(_req.content, 'html.parser')
    print(_url)
    _data_raw = _soup.find(id='archive-content')
    return _data_raw.find_all(class_='movies')


def get_data_item_json(instance, item):
    try:
        """Find the a element"""
        _data_item = item.find('a', href=True)
        """Get url"""
        _url = _data_item['href']
        """Check that the url exists"""
        _title = item.find('h3').text
        return get_node_item(item['id'].split('post-')[-1], _url, _title, instance.year, instance.host, instance.site)
    except Exception as e:
        return None


def get_list_json_items(instance, page, limit=100):
    """Declare all variables"""
    _items = list()
    """Get article html from his website"""
    _items_raw = get_data_items_raw(instance, page)
    for _item_raw in _items_raw:
        _item_data = get_data_item_json(instance, _item_raw)
        """Check if item exists"""
        if not _item_data:
            continue
        """If lang is different than en(english), add lang to slug"""
        _title = "{0}-{1}".format(_item_data['title'], instance.langname)
        """Slugify the item's title"""
        _item_data['slug'] = slugify(_title)
        """Add item"""
        _items.append(_item_data)
        """Validate if has the max"""
        if len(_items) >= limit:
            break
    """Return items"""
    return _items


def get_latest(limit=10, page=1):
    """Settings environment"""
    instance = get_instance()
    """Request to hitomi web site for latest novel"""
    _items_raw = get_list_json_items(
        instance, page, limit)
    """Validate if data exists"""
    if not _items_raw:
        """Return error if data is invalid"""
        return error_response(
            msg="Files not found."
        )
    """Response data"""
    return success_response(
        data=_items_raw
    )


def get_info_post(id):
    """Settings environment"""
    instance = get_instance()
    """Request to hitomi web site for latest novel"""
    _result = instance.get_movie_info(id)
    """Validate if data exists"""
    if not _result['valid']:
        """Return error if data is invalid"""
        return error_response(
            msg="Files not found."
        )
    """Response data"""
    return _result
