# PYTEST NON-CONTAINERIZED REQUIREMENT
import pytest, requests
from typing import Type

FPORT = 5015
BASEROUTE = f'http://localhost:{FPORT}'
requests.post(f'{BASEROUTE}/')


def test_route_perseverance():
    response = requests.get(f'{BASEROUTE}/perseverance')
    assert response.status_code == 200
    assert len(response.json())>0
    assert response.json().keys() == ["type","properties","geometry"]
    assert isinstance( response.json()["properties"]["sol"], float) == True


def test_route_sol():
    response = requests.get(f'{BASEROUTE}/perseverance/sol')
    assert response.status_code == 200
    assert isinstance( response.text, float) == True
    assert response.text[0:34] == "Most recent data waypoint is at Sol"


def test_route_ori():
    response = requests.get(f'{BASEROUTE}/perseverance/orientation')
    assert response.status_code == 200
    assert len(response.json())>0
    assert response.json().keys() == ["sol","yaw_rad","pitch","roll"]
    assert isinstance(response.json()["yaw_rad"], float) == True


def test_route_pos():
    response = requests.get(f'{BASEROUTE}/perseverance/position')
    assert response.status_code == 200
    assert len(response.json())>0
    assert response.json().keys() == ["sol","lon","lat"]
    assert isinstance(response.json()["lon"], float) == True


# ALL OTHER ROUTES ARE POST ROUTES FOR POST(ING) JOBS AND LOADERS 