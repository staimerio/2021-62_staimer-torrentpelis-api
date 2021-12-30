# Retic
from retic import env, App as app

# Requests
import requests

# Constants
URL_WORDPRESS_POSTS = app.apps['backend']['wordpress']['base_url'] + \
    app.apps['backend']['wordpress']['posts']
URL_WORDPRESS_POSTS_TYPE = app.apps['backend']['wordpress']['base_url'] + \
    app.apps['backend']['wordpress']['posts_type']

HEADERS = {
    u'oauth_consumer_key': app.config.get('WP_OAUTH_CONSUMER_KEY'),
    u'oauth_consumer_secret': app.config.get('WP_OAUTH_CONSUMER_SECRET'),
    u'oauth_token': app.config.get('WP_OAUTH_TOKEN'),
    u'oauth_token_secret': app.config.get('WP_OAUTH_TOKEN_SECRET'),
    u'base_url': app.config.get('WP_BASE_URL'),
}


def create_post(
    title,
    slug="",
    content="",
    excerpt="",
    categories=[],
    tags=[],
    meta={},
    props_resources=[],
    headers=None,
    post_type=None,
):
    """Publish a new post on the website"""

    """Prepare payload for the request"""
    _payload = {
        u"title": title,
        u"slug": slug,
        u"content": content,
        u"excerpt": excerpt,
        u"categories": categories,
        u"tags": tags,
        u"meta": meta,
        u"props_resources": props_resources,
        u"post_type": post_type,
    }

    """Build epub file"""
    _post = requests.post(
        URL_WORDPRESS_POSTS,
        json=_payload,
        headers=headers or HEADERS
    )
    """Check if the response is valid"""
    if _post.status_code != 200:
        """Return error if the response is invalid"""
        raise Exception(_post.text)
    """Get json response"""
    _post_json = _post.json()
    """Return data"""
    return _post_json


def search_post_by_slug(
    slug,
    headers=None,
    post_type=None,
):
    """Get a post on website"""

    """Prepare payload for the request"""
    _payload = {
        u"slug": slug,
        u"post_type": post_type,
    }
    """Build epub file"""
    _post = requests.get(
        URL_WORDPRESS_POSTS,
        params=_payload,
        headers=headers or HEADERS
    )
    """Check if the response is valid"""
    if _post.status_code != 200:
        """Return error if the response is invalid"""
        return None
    """Get json response"""
    _post_json = _post.json()
    """Return data"""
    return _post_json

def get_post(
    post_id,
    headers=None,
):
    """Get a post on website"""

    """Prepare payload for the request"""
    _url = "{0}/{1}".format(URL_WORDPRESS_POSTS, post_id)
    """Build epub file"""
    _post = requests.get(
        _url,
        headers=headers or HEADERS
    )
    """Check if the response is valid"""
    if _post.status_code != 200:
        """Return error if the response is invalid"""
        return None
    """Get json response"""
    _post_json = _post.json()
    """Return data"""
    return _post_json


def update_post(
    post_id,
    data=None,
    headers=None,
    post_type=None,
):
    """Update a post on website"""

    """Prepare payload for the request"""
    _url = "{0}/{1}".format(URL_WORDPRESS_POSTS, post_id)
    _payload = {
        u"data": data or {},
        u"post_type": post_type,
    }
    """Build epub file"""
    _post = requests.put(
        _url,
        json=_payload,
        headers=headers or HEADERS
    )
    """Check if the response is valid"""
    if _post.status_code != 200:
        """Return error if the response is invalid"""
        return None
    """Get json response"""
    _post_json = _post.json()
    """Return data"""
    return _post_json


def login(wp_login, wp_admin, username, password):

    with requests.Session() as session:
        headers1 = {'Cookie': 'wordpress_test_cookie=WP Cookie check'}
        data = {
            'log': username, 'pwd': password, 'wp-submit': 'Log In',
            'redirect_to': wp_admin, 'testcookie': '1'
        }
        _request=session.post(wp_login, headers=headers1, data=data)        
        return session


def request_to_ajax(url, data, session=None, headers={}):
    """Make request"""
    if session:
        _result = session.post(url, data=data, headers=headers)
    else:
        _result = requests.post(url, data=data, headers=headers)
    return _result


def create_post_type(
    post_type,
    title,
    slug="",
    content="",
    headers=None,
):
    """Publish a new post on the website"""

    """Prepare payload for the request"""
    _payload = {
        u"post_type": post_type,
        u"title": title,
        u"slug": slug,
        u"content": content,
    }

    """Build epub file"""
    _post = requests.post(
        URL_WORDPRESS_POSTS_TYPE,
        json=_payload,
        headers=headers or HEADERS
    )
    """Check if the response is valid"""
    if _post.status_code != 200:
        """Return error if the response is invalid"""
        raise Exception(_post.text)
    """Get json response"""
    _post_json = _post.json()
    """Return data"""
    return _post_json