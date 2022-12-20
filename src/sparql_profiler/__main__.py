import logging

import typer
from rdflib import Graph

from sparql_profiler import __version__
from sparql_profiler.create_dataset import create_dataset_prompt
from sparql_profiler.profiler import profile_sparql_endpoint
from sparql_profiler.utils import log

cli = typer.Typer()


@cli.command("profile")
def profile_endpoint(
    sparql_endpoint: str = typer.Argument(
        "https://graphdb.dumontierlab.com/repositories/umids-kg", help="SPARQL endpoint to profile"
    ),
    graph: str = typer.Option(
        None,
        "--graph",
        "-g",
        help="Compute metadata only for the specified graph in the triplestore (compute for all graphs by default)",
    ),
    dataset_uri: str = typer.Option(None, help="URI of the dataset distribution to describe"),
    profiler: str = typer.Option("hcls", help="Select the profiler to use: hcls or bio2rdf supported."),
    create_dataset: bool = typer.Option(
        False,
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
    if create_dataset:
        g, metadata_answers = create_dataset_prompt(sparql_endpoint, dataset_uri, g)

    g = profile_sparql_endpoint(sparql_endpoint, dataset_uri, profiler, graph, g)

    if output:
        g.serialize(destination=output, format='turtle')
        print(f"Metadata stored to {output} 📝")
    else:
        print(g.serialize(format='turtle'))


@cli.command("version")
def cli_version() -> None:
    print(__version__)


if __name__ == "__main__":
    cli()
