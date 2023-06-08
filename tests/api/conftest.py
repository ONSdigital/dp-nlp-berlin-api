import json
from dataclasses import dataclass
from unittest.mock import patch

import pytest


def load_test_code_list():
    return [{
        "change": "",
        "country": "BG",
        "subcode": "BLO",
        "name": "Lyuliakovo",
        "name_wo_diacritics": "Lyuliakovo",
        "subdivision_code": "02",
        "status": "RL",
        "function": "-----6--",
        "date": "0901",
        "iata_code": "",
        "coordinates": "4283N 02701E",
    }]

def load_test_codes():
    return [json.dumps({
        "BG": {
            "<c>": "ISO-3166-1",
            "s": "<bln|ISO-3166-1#BG|\"Bulgaria\">",
            "i": "BG",
            "d": {
                "name": "Bulgaria",
                "short": "Bulgaria",
                "alpha2": "BG",
                "alpha3": "BGR",
                "official_en": "Bulgaria",
                "official_fr": "Bulgarie",
                "continent": "EU"
            }
        }
    })]


def real_berlin_load(location):
    import berlin
    return berlin.load_from_json([load_test_codes()], load_test_code_list())

def fake_berlin_load(location):
    @dataclass
    class FakeBerlinResult:
        key: str
        encoding: str
        id: str
        words: list[str]

    class FakeBerlinDbProxy:
        def query(self, query, state, limit, lev_distance):
            return [FakeBerlinResult("A", "B", "X", ["Manchester"])]

    assert location == "data"
    return FakeBerlinDbProxy()


@pytest.fixture()
def app_with_berlin():
    with patch("app.store.load", real_berlin_load):
        from api import create_app

        app = create_app()
        app.config.update(
            {
                "TESTING": True,
            }
        )

        yield app

@pytest.fixture()
def app():
    with patch("app.store.load", fake_berlin_load):
        from api import create_app

        app = create_app()
        app.config.update(
            {
                "TESTING": True,
            }
        )

        yield app


@pytest.fixture()
def test_client_with_berlin(app_with_berlin):
    yield app_with_berlin.test_client()

@pytest.fixture()
def test_client(app):
    yield app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()
