from pathlib import Path

from app.bootstrap import bootstrap_system


def test_bootstrap_loads():
    ctx = bootstrap_system(Path('.'))
    assert 'system_config' in ctx
    assert 'plugins' in ctx
