import pytest

from flask import Flask
from game_socket import GameSocket, GameServer


@pytest.fixture()
def app():
    from app import app
    app.config['TESTING'] = True
    yield app


@pytest.fixture()
def gs():
    from app import gs
    yield gs


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def runner(app):
    return app.test_cli_runner()


@pytest.fixture
def socket_server(app):
    server = GameServer({}, {})
    return GameSocket(server, app, async_mode="threading", cors_allowed_origins="*")


def test_main_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'app' in response.data


def test_new_user(socket_server: GameSocket, app: Flask):
    # TODO: здесь должны быть тесты сокетов, но поднятие сервера что выходит за рамки unit-тестов
    pass
