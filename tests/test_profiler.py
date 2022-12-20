from sparql_profiler import __version__, profile_sparql_endpoint


def test_generate_metadata():
    sparql_endpoint_url = 'https://graphdb.dumontierlab.com/repositories/umids-kg'
    output_metadata = profile_sparql_endpoint(sparql_endpoint_url, sparql_endpoint_url, 'hcls', None)
    assert len(output_metadata) > 10


def test_version():
    """Test the version is a string."""
    assert isinstance(__version__, str)
