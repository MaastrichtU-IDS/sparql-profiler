import urllib.parse
from datetime import date

import click
from rdflib import XSD, Graph, Literal, URIRef
from rdflib.namespace import DC, DCAT, DCTERMS, FOAF, PROV, RDFS, SKOS, VOID

from sparql_profiler.namespaces import D2S, DCTYPES, IDOT, PAV, RDF, SCHEMA


def create_dataset_prompt(sparql_endpoint, distribution_uri, g=Graph(), output_file=None):
    """Create a new dataset from questions asked in the prompt"""
    metadataArray = []
    # metadataArray.append({'id': 'dataset_id', 'description': 'Enter the identifier of your datasets, e.g. drugbank (lowercase, no space or weird characters)'})
    metadataArray.append({'id': 'name', 'description': 'Enter a human-readable name for this dataset, e.g. DrugBank'})
    metadataArray.append({'id': 'description', 'description': 'Enter a description for this dataset'})
    metadataArray.append(
        {
            'id': 'downloadURL',
            'default': 'https://www.drugbank.ca/releases/5-1-1/downloads/all-full-database',
            'description': 'Enter the URL of the source data',
        }
    )
    metadataArray.append(
        {
            'id': 'license',
            'default': 'http://creativecommons.org/licenses/by-nc/4.0/legalcode',
            'description': 'Enter a valid URL to the license informations about the original dataset',
        }
    )
    metadataArray.append(
        {
            'id': 'publisher_name',
            'default': 'Institute of Data Science at Maastricht University',
            'description': 'Enter the name of the institution publishing the data and its affiliation, e.g. Institute of Data Science at Maastricht University',
        }
    )
    metadataArray.append(
        {
            'id': 'publisher_url',
            'default': 'https://maastrichtuniversity.nl/ids',
            'description': 'Enter a valid URL for the publisher homepage.',
        }
    )
    metadataArray.append(
        {'id': 'created', 'default': date.today(), 'description': 'Enter the date at which the data has been published'}
    )
    metadataArray.append(
        {'id': 'format', 'default': 'application/xml', 'description': 'Enter the format of the source data'}
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
            'default': 'http://d2s.semanticscience.org/',
            'description': 'Enter the URL of the dataset homepage',
        }
    )
    # metadataArray.append({'id': 'accessURL', 'default': 'https://www.drugbank.ca/releases/latest', 'description': 'Specify URL of the directory containing the file(s) of interest (not the direct file URL)'})
    metadataArray.append(
        {
            'id': 'references',
            'default': 'https://www.ncbi.nlm.nih.gov/pubmed/29126136',
            'description': 'Enter the URL of a publication supporting the dataset',
        }
    )
    metadataArray.append({'id': 'keyword', 'default': 'drug', 'description': 'Enter a keyword to describe the dataset'})
    # metadataArray.append({'id': 'sparqlEndpoint', 'description': 'Enter the URL of the final SPARQL endpoint to access the integrated dataset',
    #     'default': 'https://graphdb.dumontierlab.com/repositories/test-vincent'})
    # metadataArray.append({'id': 'theme', 'default': 'http://ncicb.nci.nih.gov/xml/owl/EVS/Thesaurus.owl#C54708', 'description': 'Enter the URL to an ontology concept describing the dataset theme'})

    if not distribution_uri:
        distribution_uri = click.prompt(
            click.style('[?]', bold=True) + ' Provide the distribution URI for this dataset, e.g.',
            default="https://w3id.org/d2s/drugbank/distribution",
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
                click.style('[?]', bold=True) + ' ' + metadataObject['description']
            )

    g = create_dataset(metadata_answers, sparql_endpoint, distribution_uri, g)

    if output_file:
        g.serialize(destination=output_file, format='turtle')
        print("Metadata stored to " + output_file + ' 📝')
    # else:
    #     print(g.serialize(format='turtle'))

    return g, metadata_answers


def create_dataset(metadata, sparql_endpoint, distribution_uri, g):
    """Create a new dataset from provided metadata JSON object"""
    g.bind("foaf", FOAF)
    g.bind("rdf", RDF)
    g.bind("rdfs", RDFS)
    g.bind("skos", SKOS)
    g.bind("schema", SCHEMA)
    g.bind("dcat", DCAT)
    g.bind("prov", PROV)
    g.bind("dc", DC)
    g.bind("dctypes", DCTYPES)
    g.bind("dct", DCTERMS)
    g.bind("pav", PAV)
    g.bind("idot", IDOT)
    g.bind("void", VOID)
    g.bind("d2s", D2S)
    # g.bind("owl", OWL)

    distribution_uri_slash = distribution_uri + '/' if not distribution_uri.endswith('/') else distribution_uri
    created_date = Literal(metadata['created'], datatype=XSD.date)
    lang = 'en'
    # created_date = Literal(date.today(),datatype=XSD.date)

    # Summary
    summary_uri = URIRef(f"{distribution_uri_slash}summary")
    g.add((summary_uri, RDF.type, DCTYPES['Dataset']))
    # g.add((summary_uri, RDFS['label'], Literal(metadata['name'] + ' dataset summary')))
    # g.add((summary_uri, DC.identifier, Literal(metadata['dataset_id'])))
    # g.add((summary_uri, IDOT['preferredPrefix'], Literal(metadata['dataset_id'])))
    g.add((summary_uri, DCTERMS.description, Literal(metadata['description'], lang=lang)))
    g.add((summary_uri, DCTERMS.title, Literal(metadata['name'], lang=lang)))
    g.add((summary_uri, FOAF['page'], URIRef(metadata['homepage'])))
    # g.add((summary_uri, DCAT['accessURL'], URIRef(metadata['accessURL'])))
    g.add((summary_uri, DCTERMS.references, URIRef(metadata['references'])))
    g.add((summary_uri, DCAT['keyword'], Literal(metadata['keyword'])))
    g.add((summary_uri, VOID.sparqlEndpoint, URIRef(sparql_endpoint)))

    # Publisher
    publisher_uri = URIRef(f"{distribution_uri_slash}agent/{urllib.parse.quote(metadata['publisher_name'])}")
    g.add((publisher_uri, RDF.type, DCTERMS.Agent))
    g.add((publisher_uri, FOAF['name'], Literal(metadata['publisher_name'])))
    g.add((publisher_uri, FOAF['page'], Literal(metadata['publisher_url'])))
    g.add((summary_uri, DCTERMS.publisher, publisher_uri))

    # Version
    version = '1'
    version_uri = URIRef(f"{distribution_uri_slash}version/{version}")
    g.add((version_uri, RDF.type, DCTYPES['Dataset']))
    g.add((version_uri, DCTERMS.title, Literal(f"{metadata['name']} dataset version", lang=lang)))
    g.add((version_uri, DCTERMS.description, Literal(f"{metadata['name']} dataset version", lang=lang)))
    g.add((version_uri, DCTERMS.isVersionOf, summary_uri))
    g.add((version_uri, PAV['version'], Literal(version)))
    g.add((version_uri, DCTERMS.creator, publisher_uri))
    g.add((version_uri, DCTERMS.publisher, publisher_uri))
    g.add((version_uri, DCTERMS.license, URIRef(metadata['license'])))
    g.add((version_uri, DCTERMS.language, URIRef(metadata['language'])))
    # g.add((version_uri, DCTERMS.created, created_date))

    # TODO: Add language?? With lexvo URI
    # Source distribution
    source_uri = URIRef(f"{distribution_uri_slash}version/{version}/source")
    g.add((source_uri, RDF.type, DCAT['Distribution']))
    g.add((source_uri, DCTERMS.title, Literal(f"{metadata['name']} source distribution", lang=lang)))
    g.add((source_uri, DCTERMS.description, Literal(f"{metadata['name']} source distribution", lang=lang)))
    g.add((source_uri, DCTERMS['format'], Literal(metadata['format'])))
    g.add((source_uri, DCAT['downloadURL'], URIRef(metadata['downloadURL'])))
    g.add((source_uri, DCTERMS.creator, publisher_uri))
    g.add((source_uri, DCTERMS.publisher, publisher_uri))
    g.add((source_uri, DCTERMS.license, URIRef(metadata['license'])))
    g.add((source_uri, DCTERMS.language, URIRef(metadata['language'])))
    g.add((source_uri, DCTERMS.created, created_date))
    g.add((source_uri, DCTERMS.issued, created_date))

    # RDF Distribution description
    rdf_uri = URIRef(distribution_uri)
    # rdf_uri_string = dataset_namespace + metadata['dataset_id'] + '/version/' + version + '/distribution/rdf'
    # rdf_uri = URIRef(rdf_uri_string)
    g.add((rdf_uri, RDF.type, DCAT['Distribution']))
    g.add((rdf_uri, RDF.type, VOID.Dataset))
    g.add((rdf_uri, DCTERMS.title, Literal(metadata['name'], lang=lang)))
    g.add((rdf_uri, DCTERMS.description, Literal(f"{metadata['name']} RDF distribution", lang=lang)))
    g.add((rdf_uri, DCTERMS.source, source_uri))
    g.add((rdf_uri, DCTERMS.creator, publisher_uri))
    g.add((rdf_uri, DCTERMS.publisher, publisher_uri))
    g.add((rdf_uri, DCTERMS.license, URIRef(metadata['license'])))
    # g.add((rdf_uri, DCTERMS.format, Literal('application/sparql-results+json')))
    g.add((rdf_uri, DCTERMS.format, URIRef('http://www.w3.org/ns/formats/Turtle')))
    g.add((rdf_uri, DCTERMS.language, URIRef(metadata['language'])))
    g.add((rdf_uri, DCTERMS.created, created_date))
    g.add((rdf_uri, DCTERMS.issued, created_date))

    g.add((version_uri, DCAT['distribution'], source_uri))
    g.add((version_uri, DCAT['distribution'], rdf_uri))

    if sparql_endpoint:
        g.add((rdf_uri, DCAT['accessURL'], URIRef(sparql_endpoint)))

    return g
