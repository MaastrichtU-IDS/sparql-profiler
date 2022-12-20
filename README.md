<div align="center">

# SPARQL endpoint profiler

[![PyPI - Version](https://img.shields.io/pypi/v/sparql-profiler.svg?logo=pypi&label=PyPI&logoColor=silver)](https://pypi.org/project/sparql-profiler/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/sparql-profiler.svg?logo=python&label=Python&logoColor=silver)](https://pypi.org/project/sparql-profiler/)
[![license](https://img.shields.io/pypi/l/sparql-profiler.svg?color=%2334D058)](https://github.com/MaastrichtU-IDS/sparql-profiler/blob/main/LICENSE.txt)
[![code style - black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[![Test package](https://github.com/MaastrichtU-IDS/sparql-profiler/actions/workflows/test.yml/badge.svg)](https://github.com/MaastrichtU-IDS/sparql-profiler/actions/workflows/test.yml)
[![Publish package](https://github.com/MaastrichtU-IDS/sparql-profiler/actions/workflows/publish.yml/badge.svg)](https://github.com/MaastrichtU-IDS/sparql-profiler/actions/workflows/publish.yml)

</div>

A package to profile SPARQL endpoints to extract the nodes and relations represented in the knowledge graph.

This package follows the recommendations defined by the [HCLS Community Profile](https://www.w3.org/TR/hcls-dataset/) (Health Care and Life Sciences) to generate the metadata about the content of a SPARQL endpoint.

## 📦️ Installation

This package requires Python >=3.7, simply install it with:

```shell
pip install sparql-profiler
```

## 🪄 Usage

### ⌨️ Use as a command-line interface

You can easily use your package from your terminal after installing `sparql-profiler` with pip:

```bash
sparql-profiler
```

Get a full rundown of the available options with:

```bash
sparql-profiler --help
```

Profile a SPARQL endpoint to generate [HCLS descriptive metadata](https://www.w3.org/TR/hcls-dataset/) for each graph:

```bash
sparql-profiler profile https://graphdb.dumontierlab.com/repositories/umids-kg
```

Profile a SPARQL endpoint to generate metadata specific to Bio2RDF for each graph:

```bash
d2s metadata analyze https://bio2rdf.137.120.31.102.nip.io/sparql -m bio2rdf
```

You can also add additional metadata for the dataset distribution by answering questions about it (description, license, etc) after running this command:

```bash
sparql-profiler profile https://graphdb.dumontierlab.com/repositories/umids-kg --create-dataset
```

See all options for the `profile` command with:

```bash
sparql-profiler profile --help
```

### 🐍 Use with python

 Use this package in python scripts:

 ```python
from sparql_profiler import profile_sparql_endpoint

g = profile_sparql_endpoint(
    sparql_endpoint="https://graphdb.dumontierlab.com/repositories/umids-kg",
    profiler="hcls",
)
print(g.serialize(format="turtle"))
# TODO: add example to use your package
 ```

## 🧑‍💻 Development setup

The final section of the README is for if you want to run the package in development, and get involved by making a code contribution.


### 📥️ Clone

Clone the repository:

```bash
git clone https://github.com/MaastrichtU-IDS/sparql-profiler
cd sparql-profiler
```
### 🐣 Install dependencies

Install [Hatch](https://hatch.pypa.io), this will automatically handle virtual environments and make sure all dependencies are installed when you run a script in the project:

```bash
pip install --upgrade hatch
```

Install the dependencies in a local virtual environment:

```bash
hatch -v env create
```

### 🏗️ Run in development

You can easily run the `sparql-profiler` in your terminal with hatch while in development to profile a specific SPARQL endpoint:

```bash
hatch run sparql-profile profile https://graphdb.dumontierlab.com/repositories/umids-kg
```

### ☑️ Run tests

Make sure the existing tests still work by running ``pytest``. Note that any pull requests to the fairworkflows repository on github will automatically trigger running of the test suite;

```bash
hatch run test
```

To display all `print()`:

```bash
hatch run test -s
```

### 🧹 Code formatting

The code will be automatically formatted when you commit your changes using `pre-commit`. But you can also run the script to format the code yourself:

```
hatch run fmt
```

Check the code for errors, and if it is in accordance with the PEP8 style guide, by running `flake8` and `mypy`:

```
hatch run check
```

### ♻️ Reset the environment

In case you are facing issues with dependencies not updating properly you can easily reset the virtual environment with:

```bash
hatch env prune
```

### 🏷️ New release process

The deployment of new releases is done automatically by a GitHub Action workflow when a new release is created on GitHub. To release a new version:

1. Make sure the `PYPI_TOKEN` secret has been defined in the GitHub repository (in Settings > Secrets > Actions). You can get an API token from PyPI at [pypi.org/manage/account](https://pypi.org/manage/account).
2. Increment the `version` number in the `pyproject.toml` file in the root folder of the repository.
3. Create a new release on GitHub, which will automatically trigger the publish workflow, and publish the new release to PyPI.

You can also manually trigger the workflow from the Actions tab in your GitHub repository webpage.
