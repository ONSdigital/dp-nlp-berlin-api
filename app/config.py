import time
from dynaconf import Dynaconf

current_time = int(time.time())
print(current_time)

settings = Dynaconf(
    envvar_prefix="BERLIN_API",
    load_dotenv=True, 
)

settings.reload()

HOST = settings.get("BERLIN_API_HOST", "0.0.0.0")
PORT = settings.get("BERLIN_API_PORT", 28700)

NAMESPACE = settings.get("LOGGING_NAMESPACE", "dp_nlp_berlin_api")
DATA_LOCATION = settings.get("DATA_LOCATION", "data/")

# VERSION = settings.get("VERSION", "0.1.0")
VERSION = "0.1.0"

# BERLIN_API_START_TIME name of the start_time variable
START_TIME = settings.get("START_TIME", current_time)
GIT_COMMIT = settings.get("GIT_COMMIT", "last_commit")