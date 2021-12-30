# Retic
from retic import App as app

"""Set environment file path"""
app.env.read_env('.env.production', override=True)
