# Retic
from retic import Request, Response, Next, App as app

# Services
from services.torrentpelis import torrentpelis
from retic.services.validations import validate_obligate_fields
from retic.services.responses import success_response, error_response

# Constants


WEBSITE_LIMIT_LATEST = app.config.get('WEBSITE_LIMIT_LATEST')
WEBSITE_PAGES_LATEST = app.config.get('WEBSITE_PAGES_LATEST')
WEBSITE_ORIGIN = app.config.get('WEBSITE_ORIGIN')

def publish_latest_movies(req: Request, res: Response, next: Next):
    _headers = {}

    """Validate obligate params"""
    _validate = validate_obligate_fields({
        u'wp_login': req.param('wp_login'),
        u'wp_admin': req.param('wp_admin'),
        u'wp_username': req.param('wp_username'),
        u'wp_password': req.param('wp_password'),
        u'wp_url': req.param('wp_url'),
    })

    """Check if has errors return a error response"""
    if _validate["valid"] is False:
        return res.bad_request(
            error_response(
                "The param {} is necesary.".format(_validate["error"])
            )
        )

    # """Validate obligate params"""
    _headers = {
        u'oauth_consumer_key': req.headers.get('oauth_consumer_key') or app.config.get('WP_OAUTH_CONSUMER_KEY'),
        u'oauth_consumer_secret': req.headers.get('oauth_consumer_secret') or app.config.get('WP_OAUTH_CONSUMER_SECRET'),
        u'oauth_token': req.headers.get('oauth_token') or app.config.get('WP_OAUTH_TOKEN'),
        u'oauth_token_secret': req.headers.get('oauth_token_secret') or app.config.get('WP_OAUTH_TOKEN_SECRET'),
        u'base_url': req.headers.get('base_url') or app.config.get('WP_BASE_URL'),
    }

    wp_login=req.param('wp_login')
    wp_admin=req.param('wp_admin')
    wp_username=req.param('wp_username')
    wp_password=req.param('wp_password')
    wp_url=req.param('wp_url')

    limit_publish=req.param(
        'limit_publish', app.config.get('WEBSITE_LIMIT_PUBLISH'),  callback=int)
    
    """Publish items"""
    result = torrentpelis.publish_items(
        req.param('limit', WEBSITE_LIMIT_LATEST,  callback=int),
        headers=_headers,
        wp_login=wp_login, 
        wp_admin=wp_admin, 
        wp_username=wp_username, 
        wp_password=wp_password, 
        wp_url=wp_url,
        limit_publish=limit_publish,
        page=req.param('page', WEBSITE_PAGES_LATEST, callback=int),
        origin=req.param('origin', WEBSITE_ORIGIN)
    )
    """Check if exist an error"""
    if result['valid'] is False:
        return res.bad_request(result)    
    # """Response the data to client"""
    res.ok(result)