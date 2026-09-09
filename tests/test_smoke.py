import elicitation_defense_lab as edl


def test_package_has_version():
    assert isinstance(edl.__version__, str)
    assert edl.__version__
