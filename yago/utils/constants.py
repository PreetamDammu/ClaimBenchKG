############################################################################################################
# Imports
import os

# from ..db.constants.main import YAGO_ALL_ENTITY_COUNT, YAGO_FACTS_ENTITY_COUNT

############################################################################################################
# Constants
YAGO_ENTITY_STORE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "yago_all.db")
YAGO_ENTITY_LENGTH = 49687885

YAGO_PREFIXES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db/yago-prefixes.txt")

YAGO_ENDPOINT_URL = "http://localhost:9999/bigdata/sparql"


