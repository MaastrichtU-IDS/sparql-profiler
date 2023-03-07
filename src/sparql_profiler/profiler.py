import os
import re
from datetime import date
from typing import Any, Optional

import pkg_resources
from rdflib import XSD, Graph, Literal, URIRef
from rdflib.namespace import DC, DCAT, DCTERMS, FOAF, PROV, SKOS, VOID
from SPARQLWrapper import JSON, TURTLE, SPARQLWrapper

from sparql_profiler.namespaces import DCTYPES, IDOT, PAV, SCHEMA
from sparql_profiler.utils import BLUE, BOLD, END, GREEN, RED, YELLOW, log, query_prefixes


class SparqlProfiler:
    def __init__(
        self,
        endpoint_url: str,
        profiler_type: str = "hcls",
        focus_graph: Optional[str] = None,
        metadata: Graph = Graph(),
    ) -> None:
        self.endpoint_url = endpoint_url.rstrip('/').rstrip('#')
        self.sparql_wrapper = SPARQLWrapper(self.endpoint_url)
        self.profiler_type = profiler_type
        self.focus_graph = focus_graph
        self.metadata = metadata
        self.metadata.bind("foaf", FOAF)
        self.metadata.bind("skos", SKOS)
        self.metadata.bind("schema", SCHEMA)
        self.metadata.bind("dcat", DCAT)
        self.metadata.bind("prov", PROV)
        self.metadata.bind("dc", DC)
        self.metadata.bind("dctypes", DCTYPES)
        self.metadata.bind("dct", DCTERMS)
        self.metadata.bind("pav", PAV)
        self.metadata.bind("idot", IDOT)
        self.metadata.bind("void", VOID)
        self.profile_endpoint()

    def profile_endpoint(self) -> None:
        """Query the provided SPARQL endpoint to compute metadata"""
        log.info(f"🔎 Profiling the SPARQL endpoint {BOLD}{self.endpoint_url}{END}")

        # If no specific graph provided we get graphs from the SPARQL endpoint
        if not self.focus_graph:
            query_select_all_graphs = 'SELECT DISTINCT ?graph WHERE { GRAPH ?graph {?s ?p ?o} }'
            self.sparql_wrapper.setQuery(query_select_all_graphs)
            self.sparql_wrapper.setReturnFormat(JSON)
            results: Any = self.sparql_wrapper.query().convert()
            # print('Get all graphs query Results:')
            # print(results)
            select_all_graphs_results = results["results"]["bindings"]
            log.info(
                f"Computing metadata for all {BOLD}{RED}{len(select_all_graphs_results)}{END} graphs in the endpoint"
            )
        else:
            # Just query the single provided graph
            select_all_graphs_results = [{'graph': {'value': self.focus_graph}}]

        # Compute metadata per graph
        for graph_row in select_all_graphs_results:
            graph = graph_row['graph']['value']

            log.info(f"⏳️ Computing metadata for graph {BOLD}{BLUE}{graph}{END}")
            if self.profiler_type == 'optimized':
                self.get_classes_relations(graph)
            elif self.profiler_type == 'hcls' or self.profiler_type == 'bio2rdf':
                self.run_non_optimized_queries(graph)
            else:
                raise ValueError(
                    f"Profiler {self.profiler_type} not recognized, must be one of: optimized, hcls, bio2rdf"
                )

        issued_date = Literal(date.today(), datatype=XSD.date)
        self.metadata.add((URIRef(self.endpoint_url), DCTERMS.issued, issued_date))

    # TODO: optimize this function
    def get_classes_relations(self, graph: Optional[str] = None) -> None:
        """Get the relations between classes in the graph
        It specifies the number of unique subject types that are linked to unique object types in the dataset:
        """
        if graph:
            graph_start = f"GRAPH <{graph}> {{"
            graph_end = '}'
        else:
            graph_start = ""
            graph_end = ""
            graph = self.endpoint_url

        # NOTE: we need to escape curly brackets {} in the query by doubling them
        query = f"""{query_prefixes}
CONSTRUCT {{
  <{graph}> a void:Dataset ;
    void:propertyPartition [
      void:property ?p ;
      void:classPartition [
        void:class ?stype ;
        void:distinctSubjects ?scount ;
      ];
      void-ext:objectClassPartition [
        void:class ?otype ;
        void:distinctObjects ?ocount ;
      ];
    ] .
  #?stype rdfs:label ?slabel .
  #?otype rdfs:label ?olabel .
}} WHERE {{
  {graph_start}
    SELECT (COUNT(DISTINCT ?s) AS ?scount) ?stype ?p ?otype  (COUNT(DISTINCT ?o) AS ?ocount)
    {{
      ?s ?p ?o .
      ?s a ?stype .
      ?o a ?otype .
    }} GROUP BY ?p ?stype ?otype
  {graph_end}
  #OPTIONAL {{ ?stype rdfs:label ?slabel }}
  #OPTIONAL {{ ?otype rdfs:label ?olabel }}
}}
"""
        # TODO: to optimize and scale, for example you could:
        # 1. query to get the list of all distinct subjects that have a type
        # 2. iterate this list, and send a query for each subject to get the classes relations for this subject
        # 3. do the same for the objects

        log.debug(query)
        self.sparql_wrapper.setQuery(query)
        self.sparql_wrapper.setReturnFormat(TURTLE)
        # self.sparql_wrapper.setReturnFormat(JSON)
        results: Any = self.sparql_wrapper.query().convert()

        # When using SELECT queries:
        # for result in results["results"]["bindings"]:
        #     print(result['stype']["value"])

        self.metadata.parse(data=results, format="turtle")
        log.info(f"✅ Classes relations successfully extracted for graph {graph}")

    def run_non_optimized_queries(self, graph: str) -> None:
        """Old function to run non optimized HCLS queries to compute metadata for an endpoint
        But this does not scale well and need to be rewritten
        """
        for filename in os.listdir(pkg_resources.resource_filename('sparql_profiler', 'queries/' + self.profiler_type)):
            log.info(f"Running query {BOLD}{YELLOW}{filename}{END} on graph {BOLD}{GREEN}{graph}{END}")
            with open(
                pkg_resources.resource_filename('sparql_profiler', 'queries/' + self.profiler_type + '/' + filename)
            ) as f:
                sparql_query = f.read()

                # Define variables to replace for the different metadata type here
                if self.profiler_type == 'bio2rdf':
                    namespace_search = re.search(
                        r'http:\/\/bio2rdf\.org\/(.*)_resource:bio2rdf\.dataset\.(.*)\.R[0-9]*', graph, re.IGNORECASE
                    )
                    if namespace_search:
                        graph_namespace = namespace_search.group(1)
                        sparql_query = sparql_query.replace('?_graph_namespace', graph_namespace)
                    # extract namespace from graph URI

                if self.profiler_type == 'hcls':
                    if graph:
                        sparql_query = sparql_query.replace('?_graph_uri', graph)
                        sparql_query = sparql_query.replace('<?_graph_start>', 'GRAPH <' + graph + '> {')
                        sparql_query = sparql_query.replace('<?_graph_end>', '}')
                    else:
                        sparql_query = sparql_query.replace('?_graph_uri', self.endpoint_url)
                        sparql_query = sparql_query.replace('<?_graph_start>', '')
                        sparql_query = sparql_query.replace('<?_graph_end>', '')

                complete_query = query_prefixes + sparql_query
                log.debug(complete_query)
                try:
                    self.sparql_wrapper.setQuery(complete_query)
                    self.sparql_wrapper.setReturnFormat(TURTLE)
                    results: Any = self.sparql_wrapper.query().convert()

                    self.metadata.parse(data=results, format="turtle")
                    log.info(f"✅ Query {filename} successfully executed on graph {graph}")

                except Exception as e:
                    log.info(f"❌ Query {BOLD}{RED}{filename}{END} failed on graph {BOLD}{YELLOW}{graph}{END}")
                    log.info(complete_query)
                    log.info(f"{BOLD}{RED}{e}{END}")
