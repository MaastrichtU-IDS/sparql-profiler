import os
import re

import pkg_resources
from rdflib import Graph
from SPARQLWrapper import JSON, TURTLE, SPARQLWrapper

from sparql_profiler.utils import BLUE, BOLD, END, GREEN, RED, YELLOW, log


def profile_sparql_endpoint(sparql_endpoint, rdf_distribution_uri, metadata_type, graph, g=Graph()):
    """Query the provided SPARQL endpoint to compute HCLS metadata"""
    log.info(f"🔎 Executing queries to profile the SPARQL endpoint {BOLD}{sparql_endpoint}{END}")
    sparql = SPARQLWrapper(sparql_endpoint)

    query_prefixes = """PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
PREFIX dqv: <http://www.w3.org/ns/dqv#>
PREFIX hcls: <http://www.w3.org/hcls#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dctypes: <http://purl.org/dc/dcmitype/>
PREFIX dcat: <http://www.w3.org/ns/dcat#>
PREFIX void: <http://rdfs.org/ns/void#>
PREFIX void-ext: <http://ldf.fi/void-ext#>\n"""

    # If no specific graph provided we get graphs from the SPARQL endpoint
    if not graph:
        query_select_all_graphs = 'SELECT DISTINCT ?graph WHERE { GRAPH ?graph {?s ?p ?o} }'
        sparql.setQuery(query_select_all_graphs)
        sparql.setReturnFormat(JSON)
        results = sparql.query().convert()
        # print('Get all graphs query Results:')
        # print(results)
        select_all_graphs_results = results["results"]["bindings"]
    else:
        # Just query the single provided graph
        select_all_graphs_results = [{'graph': {'value': str(graph)}}]

    # Compute HCLS metadata per graph
    for graph_row in select_all_graphs_results:
        graph = graph_row['graph']['value']

        log.info(f"🕸️  Computing metadata for graph {BOLD}{BLUE}{graph}{END}")
        for filename in os.listdir(pkg_resources.resource_filename('sparql_profiler', 'queries/' + metadata_type)):
            log.info(f"⏳️ Running query {BOLD}{YELLOW}{filename}{END} on graph {BOLD}{GREEN}{graph}{END}")
            with open(
                pkg_resources.resource_filename('sparql_profiler', 'queries/' + metadata_type + '/' + filename)) as f:
                sparql_query = f.read()

                # Define variables to replace for the different metadata type here
                if metadata_type == 'bio2rdf':
                    namespace_search = re.search(
                        r'http:\/\/bio2rdf\.org\/(.*)_resource:bio2rdf\.dataset\.(.*)\.R[0-9]*', graph, re.IGNORECASE
                    )
                    if namespace_search:
                        graph_namespace = namespace_search.group(1)
                        sparql_query = sparql_query.replace('?_graph_namespace', graph_namespace)
                    # extract namespace from graph URI

                if metadata_type == 'hcls':
                    if graph:
                        sparql_query = sparql_query.replace('?_graph_uri', graph)
                        sparql_query = sparql_query.replace('<?_graph_start>', 'GRAPH <' + graph + '> {')
                        sparql_query = sparql_query.replace('<?_graph_end>', '}')
                    else:
                        sparql_query = sparql_query.replace('?_graph_uri', rdf_distribution_uri)
                        sparql_query = sparql_query.replace('<?_graph_start>', '')
                        sparql_query = sparql_query.replace('<?_graph_end>', '')

                complete_query = query_prefixes + sparql_query
                log.debug(complete_query)

                try:
                    sparql.setQuery(complete_query)
                    sparql.setReturnFormat(TURTLE)
                    # sparql.setReturnFormat(JSONLD)
                    results = sparql.query().convert()

                    g.parse(data=results, format="turtle")
                    # g.parse(data=results, format="json-ld")
                    log.info(f"✅ Query {filename} successfully executed on graph {graph}")

                except Exception as e:
                    log.info(f"❌ Query {BOLD}{RED}{filename}{END} failed on graph {BOLD}{YELLOW}{graph}{END}")
                    log.info(complete_query)
                    log.info(f"{BOLD}{RED}{e}{END}")

    return g
