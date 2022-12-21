import logging

log = logging.getLogger()


# Variables to make the prints gorgeous:
BOLD = '\033[1m'
END = '\033[0m'
GREEN = '\033[32m'
YELLOW = '\033[33m'
RED = '\033[91m'
BLUE = '\033[34m'
# CYAN = '\033[36m' PURPLE = '\033[95m' BLUE = '\033[34m'


query_prefixes = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX hcls: <http://www.w3.org/hcls#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dctypes: <http://purl.org/dc/dcmitype/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX void-ext: <http://ldf.fi/void-ext#>
"""

# To avoid cluttering the metadata generated with useless metadata
# that does not represent the content of the KG
skip_manufacturer_graphs = [
    "http://www.openlinksw.com/schemas/virtrdf#",
    "b3sonto",
    "http://localhost:8890/sparql",
    "http://localhost:8890/DAV/",
    "b3sifp",
    "urn:rules.skos",
    "http://www.openlinksw.com/schemas/oplweb#",
    "virtrdf-label",
    "facets",
]
