############################################################################################################
# Imports
import os

############################################################################################################
# Constants
YAGO_ENTITY_STORE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "yago_all.db")
YAGO_ENTITY_LENGTH = 49687885

YAGO_PREFIXES_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "db/yago-prefixes.txt")

YAGO_ENDPOINT_URL = "http://localhost:9999/bigdata/sparql"

PREFIXES = {
    "yago": "http://yago-knowledge.org/resource/",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "schema": "http://schema.org/"
}

INVALID_PROPERTIES = {
    "schema:url",
    "rdfs:comment"
}
