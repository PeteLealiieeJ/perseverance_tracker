# PYTEST NON-CONTAINERIZED REQUIREMENT
import pytest, requests
from typing import Type

FPORT = 5015
BASEROUTE = f'http://localhost:{FPORT}'
requests.post(f'{BASEROUTE}/load')


def test_route_perseverance():
    response = requests.get(f'{BASEROUTE}/perseverance')
    assert response.status_code == 200
    assert len(response.json())>0
    assert list( response.json()[0].keys() ) == ["type","properties","geometry"]
    assert isinstance( response.json()[0]["properties"]["sol"], int) == True


def test_route_sol():
    response = requests.get(f'{BASEROUTE}/perseverance/sol')
    assert response.status_code == 200
    assert isinstance( str(response.text), str) == True
    assert str(response.text[0:35]) == "Most recent data waypoint is at Sol"


def test_route_ori():
    response = requests.get(f'{BASEROUTE}/perseverance/orientation')
    assert response.status_code == 200
    assert len(response.json())>0
    assert list( response.json()[0].keys() ) == ["sol","yaw_rad","pitch","roll"]
    assert isinstance(response.json()[0]["yaw_rad"], float) == True


def test_route_pos():
    response = requests.get(f'{BASEROUTE}/perseverance/position')
    assert response.status_code == 200
    assert len(response.json())>0
    assert list( response.json()[0].keys() ) == ["sol","lon","lat"]
    assert isinstance(response.json()[0]["lon"], float) == True


# ALL OTHER ROUTES ARE POST ROUTES FOR POST(ING) JOBS AND LOADERS 
