import importlib


def test_import_api_module():
    # simple smoke test: ensure the module imports and exposes `app` for ASGI
    m = importlib.import_module("api.index")
    assert hasattr(m, "app")
