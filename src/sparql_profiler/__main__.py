import logging

import typer
from rdflib import Graph

from sparql_profiler import __version__
from sparql_profiler.profiler import SparqlProfiler
from sparql_profiler.questions import get_metadata_from_prompt
from sparql_profiler.utils import log

cli = typer.Typer()


@cli.command("profile")
def profile_endpoint(
    sparql_endpoint: str = typer.Argument(
        "https://graphdb.dumontierlab.com/repositories/umids-kg", help="SPARQL endpoint to profile"
    ),
    focus_graph: str = typer.Option(
        None,
        "--focus-graph",
        "-g",
        help="Compute metadata only for the specified graph in the triplestore (compute for all graphs by default)",
    ),
    profiler: str = typer.Option("optimized", help="Select the profiler to use among: optimized, hcls, bio2rdf."),
    questions: bool = typer.Option(
        False,
        "--questions",
        "-q",
        help="Prompt questions to generate the dataset metadata and analyze the endpoint (default), or only analyze",
    ),
    output: str = typer.Option(
        None, "--output", "-o", help="Path to the output file, will be displayed in the terminal if not specified."
    ),
    log_level: str = typer.Option("INFO", "--log", "-l", help="Log level displayed: DEBUG, INFO, ERROR"),
) -> None:
    """Generate descriptive metadata (about types and relations) for the graphs in a SPARQL endpoint"""
    # Setup logger
    log.setLevel(logging.getLevelName(log_level.upper()))
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s %(levelname)s: %(message)s")
    # formatter = logging.Formatter("%(asctime)s %(levelname)s: [%(module)s:%(funcName)s] %(message)s")
    console_handler.setFormatter(formatter)
    log.addHandler(console_handler)

    g = Graph()
    if questions:
        g = get_metadata_from_prompt(sparql_endpoint, g)

    sp = SparqlProfiler(sparql_endpoint, profiler, focus_graph, g)

    if output:
        sp.metadata.serialize(destination=output, format='turtle')
        log.info(f"Metadata stored to {output} 📝")
    else:
        log.info(sp.metadata.serialize(format='turtle'))


@cli.command("version")
def cli_version() -> None:
    print(__version__)


if __name__ == "__main__":
    cli()
