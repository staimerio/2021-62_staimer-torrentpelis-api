"""Services for novels controller"""

# Retic
from retic import env, App as app

# Requests
import requests

# Time
from time import sleep
# Time
from datetime import datetime

# Services
from retic.services.responses import success_response, error_response
# services
from services.wordpress import wordpress

# Models
from models import Scrapper
import services.general.constants as constants
import services.movies.movies as movies

# Constants
WEBSITE_LIMIT_LATEST = app.config.get('WEBSITE_LIMIT_LATEST')
WEBSITE_POST_TYPE = app.config.get('WEBSITE_POST_TYPE')

URL_CINECALIDAD_LATEST = app.apps['backend']['cinecalidad']['base_url'] + \
    app.apps['backend']['cinecalidad']['latest']
URL_CINECALIDAD_POST = app.apps['backend']['cinecalidad']['base_url'] + \
    app.apps['backend']['cinecalidad']['posts']

URL_TMDB_SEARCH = app.apps['backend']['tmdb']['base_url'] + \
    app.apps['backend']['tmdb']['search']


def get_items_from_origin(limit, page, origin=None):
    if origin == constants.ORIGIN['cinecalidad']:
        return get_items_from_website(limit, page, origin)
    elif origin == constants.ORIGIN['torrentpelis']:
        _items = movies.get_latest(
            limit=limit,
            page=page,
        )
        if not _items['valid']:
            return _items
        return success_response(data={u'items': _items['data']})
    else:
        return get_items_from_website(limit, page, origin)


def get_publication_from_origin(url, id, origin):
    if origin == constants.ORIGIN['cinecalidad']:
        """Get all chapters of the novels without ids that exists"""
        return get_mirrors_from_website(
            url_base=URL_CINECALIDAD_POST,
            url=url,
            id=id
        )
    elif origin == constants.ORIGIN['torrentpelis']:
        _publication = movies.get_info_post(
            id=id
        )
        return _publication['data']
    else:
        return None


def get_items_from_website(limit, page, origin):
    """Prepare the payload"""
    _payload = {
        u"limit": limit,
        u"page": page
    }
    """Get all novels from website"""
    _result = requests.get(URL_CINECALIDAD_LATEST, params=_payload)
    """Check if the response is valid"""
    if _result.status_code != 200:
        """Return error if the response is invalid"""
        raise Exception(_result.text)
    """Get json response"""
    _result_json = _result.json()
    """Return novels"""
    return _result_json


def get_mirrors_from_website(url_base, url, id):
    """Prepare the payload"""
    _payload = {
        u"url": url,
        u"id": id,
    }
    """Get all chapters from website"""
    _info = requests.get(url_base, params=_payload)
    """Check if the response is valid"""
    if _info.status_code != 200:
        """Return error if the response is invalid"""
        return None
    """Get json response"""
    _info_json = _info.json()
    """Return chapters"""
    return _info_json.get('data')


def get_info_from_tmdb(term):
    """Prepare the payload"""
    _payload = {
        u"term": term,
    }
    """Get all chapters from website"""
    _info = requests.get(URL_TMDB_SEARCH, params=_payload)
    """Check if the response is valid"""
    if _info.status_code != 200:
        """Return error if the response is invalid"""
        return None
    """Get json response"""
    _info_json = _info.json()
    """Return chapters"""
    return _info_json.get('data')


def build_items_to_upload(
    items,
    headers,
    limit_publish,
    origin,
    session, url_admin,
):
    """Define all variables"""
    _items = []
    """For each novel do the following"""
    for _item in items:
        """Find novel in db"""
        _oldpost = wordpress.search_post_by_slug(
            _item['slug'], headers=headers, post_type=WEBSITE_POST_TYPE
        )
        if _oldpost:
            continue

        _publication = get_publication_from_origin(
            _item['url'], _item['id'], origin)
        """Check if it has any problem"""
        if not _publication or not _publication['mirrors']:
            continue

        """Get information from tmdb"""
        _info = get_info_from_tmdb(
            term=_publication['title'],
        )

        if not _info or not _info['imdb_id']:
            continue

        """Add payload"""
        _params_item = {
            'tmdbid': _info['imdb_id'],
            'typept': 'movies',
            'validate': True,
            'action': 'dbmovies_genereditor'
        }
        _req = wordpress.request_to_ajax(url_admin, _params_item, session)
        """Get json"""
        _item_imported = _req.json()

        """If it was published, then add"""
        if not _item_imported or ('response' in _item_imported and _item_imported['response']):
            continue

        """Set data"""
        _data = {
            **_item,
            **_publication,
            **_info,
        }
        """Add novel to list"""
        _items.append(_data)
        """Check the limit"""
        if len(_items) >= limit_publish:
            break
    return _items


def publish_item_wp(
    items, headers,
    session, url_admin,
):
    """Publish all items but it check if the post exists,
    in this case, it will update the post.

    :param items: List of novel to will publish
    """

    """Define all variables"""
    _published_items = []
    """For each novels do to the following"""
    for _item in items:
        """Create the post"""
        _post = wordpress.create_post(
            post_type=WEBSITE_POST_TYPE,
            title=_item['title'],
            slug=_item['slug'],
            headers=headers,
        )
        """Check if is a valid post"""
        if not _post or not _post['valid'] or not 'id' in _post['data']:
            """Add post to novel"""
            print(
                "if not _post or not _post['valid'] or not 'id' in _post['data']")
            continue

        """Add payload"""
        _params_item = {
            'idpost': _post['data']['id'],
            'tmdbid': _item['imdb_id'],
            'typept': 'movies',
            'action': 'dbmovies_genereditor'
        }
        _req = wordpress.request_to_ajax(url_admin, _params_item, session)
        """Get json"""
        _item_imported = _req.json()

        """If it was published, then add"""
        if not _item_imported['response']:
            _post_updated = wordpress.update_post(
                _post['data']['id'],
                {
                    u'status': 'trash'
                },
                headers=headers,
                post_type=WEBSITE_POST_TYPE,
            )
            continue
        else:
            _post_updated = wordpress.update_post(
                _post['data']['id'],
                {
                    u'status': 'publish'
                },
                headers=headers,
                post_type=WEBSITE_POST_TYPE,
            )

        """Upload links"""
        for _mirror in _item['mirrors']:
            """Add payload"""
            _params_item = {
                'urls': _mirror['url'],
                'type': 'Torrent',
                'quality': _mirror['quality'],
                'language': _mirror['lang'],
                'size': _mirror['size'],
                'postid': _post['data']['id'],
                'action': 'doosave_links'
            }
            _req_mirrors = wordpress.request_to_ajax(
                url_admin, _params_item, session)
        _item_published = {
            'post_id': _post['data']['id'],
            'slug': _item['slug'],
            'title': _item['title'],
            'mirror': _item['mirrors']
        }
        _published_items.append(_item_published)
    """Return the posts list"""
    return _published_items


def upload_items(
    limit,
    headers,
    wp_login, wp_admin, wp_username, wp_password, wp_url,
    limit_publish,
    page,
    origin,
):
    _items = get_items_from_origin(
        limit=limit,
        page=page,
        origin=origin,
    )

    if _items['valid'] is False:
        print("if _items['valid'] is False")
        return []

    _session = wordpress.login(
        wp_login, wp_admin, wp_username, wp_password)

    _url_admin = '{0}/wp-admin/admin-ajax.php'.format(
        wp_url)

    _builded_items = build_items_to_upload(
        _items['data']['items'],
        headers,
        limit_publish,
        origin=origin,
        session=_session,
        url_admin=_url_admin,
    )

    if not _builded_items:
        print("if not _builded_items")
        return []

    """Publish or update on website"""
    _created_posts = publish_item_wp(
        _builded_items,
        headers=headers,
        session=_session,
        url_admin=_url_admin,
    )
    return _created_posts


def publish_items(
    limit,
    headers,
    wp_login, wp_admin, wp_username, wp_password, wp_url,
    limit_publish,
    page=1,
    origin=None
):
    _items = []
    """Find in database"""
    _session = app.apps.get("db_sqlalchemy")()
    _item = _session.query(Scrapper).\
        filter(Scrapper.key == wp_url, Scrapper.type == constants.TYPES['movies']).\
        first()

    _date = datetime.now()

    if not _item or (_item.created_at.year != _date.year or _item.created_at.day != _date.day):
        print("*********upload_items*********")
        _items = upload_items(
            limit,
            headers,
            wp_login, wp_admin, wp_username, wp_password, wp_url,
            limit_publish,
            page=page,
            origin=origin,
        )
    print("*********len(_items)*********:" + str(len(_items)))
    """Check if almost one item was published"""
    if(len(_items) == 0):
        """Find in database"""
        _session = app.apps.get("db_sqlalchemy")()
        _item = _session.query(Scrapper).\
            filter(Scrapper.key == wp_url, Scrapper.type == constants.TYPES['movies']).\
            first()

        print("*********if _item is None*********")
        if _item is None:
            print("*********_item = Scrapper*********")
            _item = Scrapper(
                key=wp_url,
                type=constants.TYPES['movies'],
                value=page+1
            )
            """Save chapters in database"""
            _session.add(_item)
            _session.flush()

        _items = upload_items(
            limit,
            headers,
            wp_login, wp_admin, wp_username, wp_password, wp_url,
            limit_publish,
            page=_item.value,
            origin=origin,
        )

        if(len(_items) == 0):
            print("*********_item.value = *********")
            _item.value = str(int(_item.value)+1)

        _session.commit()
        _session.close()

    _data_respose = {
        u"items":  _items
    }
    return success_response(
        data=_data_respose
    )
