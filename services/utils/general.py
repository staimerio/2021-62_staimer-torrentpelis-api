"""Services for general utils"""

# Services
from retic.services.general.urls import slugify


def get_node_item(id, url, title, year, host, site=''):
    """Set item structure"""
    _item = {
        u'id': id,
        u'url': url,
        u'title': title,
        u'year': int(year),
        u'service': host,
        u'site': site
    }
    return _item

def outmarks(s):
    s = s.replace('\n', '')
    s = s.replace('\r', '')
    s = s.replace('\"', '\'')
    return s