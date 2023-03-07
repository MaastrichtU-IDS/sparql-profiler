from typing import Dict

import click
from rdflib import RDF, Graph, Literal, URIRef
from rdflib.namespace import DCAT, DCTERMS, FOAF, VOID


def get_metadata_from_prompt(
    sparql_endpoint: str,
    g: Graph = Graph(),
) -> Graph:
    """Create a new dataset from questions asked in the prompt"""
    metadataArray = []
    metadataArray.append({'id': 'name', 'description': 'Enter a human-readable name for this dataset, e.g. DrugBank'})
    metadataArray.append({'id': 'description', 'description': 'Enter a description for this dataset'})
    metadataArray.append(
        {
            'id': 'license',
            'default': 'http://creativecommons.org/licenses/by-nc/4.0/legalcode',
            'description': 'Enter a valid URL to the license informations about the endpoint data',
        }
    )
    metadataArray.append(
        {
            'id': 'download_url',
            'description': 'Enter a URL where to download the endpoint data as dump.',
        }
    )
    metadataArray.append(
        {
            'id': 'publisher_url',
            'description': 'Enter a valid URL for the publisher homepage.',
        }
    )
    metadataArray.append(
        {
            'id': 'publisher_name',
            'description': 'Enter the name of the institution publishing the data and its affiliation, e.g. Institute of Data Science at Maastricht University',
        }
    )
    metadataArray.append(
        {
            'id': 'language',
            'default': 'http://lexvo.org/id/iso639-3/eng',
            'description': 'Enter the lexvo URI for the language of the data',
        }
    )
    metadataArray.append(
        {
            'id': 'homepage',
            'description': 'Enter the URL of the dataset homepage',
        }
    )
    metadataArray.append(
        {
            'id': 'references',
            'description': 'Enter the URL of a publication supporting the dataset',
        }
    )
    metadataArray.append(
        {
            'id': 'keywords',
            'description': 'Enter keywords describing the dataset (each keyword separated by a comma)',
        }
    )
    metadata_answers = {}
    for metadataObject in metadataArray:
        if 'default' in metadataObject:
            metadata_answers[metadataObject['id']] = click.prompt(
                click.style('[?]', bold=True) + ' ' + metadataObject['description'] + ' e.g.',
                default=metadataObject['default'],
            )
        else:
            metadata_answers[metadataObject['id']] = click.prompt(
                click.style('[?]', bold=True) + ' ' + metadataObject['description'], default='', show_default=False
            )

    g = add_prompt_to_graph(metadata_answers, sparql_endpoint, g)

    return g


def add_prompt_to_graph(answers: Dict[str, str], endpoint_url: str, g: Graph = Graph()) -> Graph:
    """Create a new dataset from provided metadata JSON object"""
    endpoint_url = endpoint_url.rstrip('/').rstrip('#')
    endpoint_uri = URIRef(endpoint_url)
    lang = 'en'

    # Add publisher info
    if answers['publisher_url']:
        publisher_uri = URIRef(answers['publisher_url'])
        g.add((publisher_uri, RDF.type, DCTERMS.Agent))
        if answers['publisher_name']:
            g.add((publisher_uri, FOAF['name'], Literal(answers['publisher_name'])))
        g.add((publisher_uri, FOAF['page'], publisher_uri))
        g.add((endpoint_uri, DCTERMS.publisher, publisher_uri))

    # Add infos about the SPARQL distribution
    g.add((endpoint_uri, RDF.type, DCAT['Distribution']))
    g.add((endpoint_uri, RDF.type, VOID.Dataset))
    g.add((endpoint_uri, DCAT['accessURL'], endpoint_uri))
    if answers['name']:
        g.add((endpoint_uri, DCTERMS.title, Literal(answers['name'], lang=lang)))
    if answers['description']:
        g.add((endpoint_uri, DCTERMS.description, Literal(answers['description'], lang=lang)))
    if answers['license']:
        g.add((endpoint_uri, DCTERMS.license, URIRef(answers['license'])))
    if answers['language']:
        g.add((endpoint_uri, DCTERMS.language, URIRef(answers['language'])))
    if answers['download_url']:
        g.add((endpoint_uri, DCAT['downloadURL'], URIRef(answers['download_url'])))
    if answers['homepage']:
        g.add((endpoint_uri, FOAF.page, URIRef(answers['homepage'])))
    if answers['references']:
        g.add((endpoint_uri, DCTERMS.references, URIRef(answers['references'])))
    if answers['keywords']:
        for keyword in answers['keywords'].split(","):
            g.add((endpoint_uri, DCAT['keyword'], Literal(keyword)))

    return g
