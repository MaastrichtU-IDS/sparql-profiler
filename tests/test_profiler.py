from sparql_profiler import SparqlProfiler, __version__


def test_profiler_optimized():
    sparql_endpoint_url = 'https://graphdb.dumontierlab.com/repositories/umids-kg'
    sp = SparqlProfiler(sparql_endpoint_url)
    assert len(sp.metadata) > 8


def test_profiler_hcls():
    sparql_endpoint_url = 'https://graphdb.dumontierlab.com/repositories/umids-kg'
    sp = SparqlProfiler(sparql_endpoint_url, 'hcls')
    assert len(sp.metadata) > 10


def test_version():
    """Test the version is a string."""
    assert isinstance(__version__, str)
