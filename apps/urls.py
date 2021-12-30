# Retic
from retic import App as app

"""Define all other apps"""
BACKEND_CINECALIDAD = {
    u"base_url": app.config.get('APP_BACKEND_CINECALIDAD'),
    u"latest": "/movies/latest",
    u"posts": "/movies/posts",
}

BACKEND_WORDPRESS = {
    u"base_url": app.config.get('APP_BACKEND_WORDPRESS'),
    u"posts": "/posts",
    u"posts_type": "/posts-type",
}

BACKEND_TMDB = {
    u"base_url": app.config.get('APP_BACKEND_TMDB'),
    u"search": "/search",
}

APP_BACKEND = {
    u"cinecalidad": BACKEND_CINECALIDAD,
    u"wordpress": BACKEND_WORDPRESS,
    u"tmdb": BACKEND_TMDB,
}

"""Add Backend apps"""
app.use(APP_BACKEND, "backend")
