# Retic
from retic import Router

# Controllers
import controllers.torrentpelis as torrentpelis
import controllers.movies as movies

router = Router()

# Anime
router.post("/torrentpelis/movies", torrentpelis.publish_latest_movies)

router.get("/movies/latest", movies.get_latest)
router.get("/movies/posts", movies.get_info_post)