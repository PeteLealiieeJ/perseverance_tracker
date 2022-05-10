# PYTEST NON-CONTAINERIZED REQUIREMENT
import pytest, requests
from typing import Type

FPORT = 5015
BASEROUTE = f'http://localhost:{FPORT}'
requests.post(f'{BASEROUTE}/')


def test_route_perseverance():
    response = requests.get(f'{BASEROUTE}/perseverance')
    assert response.status_code == 200
    assert


def test_route_sol():
    response = requests.get(f'{BASEROUTE}/perseverance/sol')
    assert response.status_code == 200


def test_route_pos():
    response = requests.get(f'{BASEROUTE}/perseverance/position')
    assert response.status_code == 200
