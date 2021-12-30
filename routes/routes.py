# Retic
from retic import Router

# Controllers
import controllers.torrentpelis as torrentpelis

router = Router()

# Anime
router.post("/torrentpelis/movies", torrentpelis.publish_latest_movies)