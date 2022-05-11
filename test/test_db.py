# PYTEST NON-CONTAINERIZED REQUIREMENT
import pytest, requests
from redis import StrictRedis
from typing import Type
import json
import sys, os

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(f'{parentdir}/src')

from jobs import generate_way_key, generate_trav_key

FPORT = 5015
BASEROUTE = f'http://localhost:{FPORT}'
requests.post(f'{BASEROUTE}/load')

# MUST BE CHANGED EVERYTIME CONTAINER ISN'T SET
REDIS_TEST_IP = '172.17.0.31'
REDIS_TEST_PORT = 6379

WAYDATA_REDIS_DB = 0
TRAVDATA_REDIS_DB = 1

rdw = StrictRedis(host=REDIS_TEST_IP, port=REDIS_TEST_PORT, db=WAYDATA_REDIS_DB)
rdt = StrictRedis(host=REDIS_TEST_IP, port=REDIS_TEST_PORT, db=TRAVDATA_REDIS_DB)


# WAYPOINT DATABASE TESTS
def test_rdatabase_way():
    assert len(rdw.keys())>0
    assert list(rdw.keys())[0].decode('utf-8')[0:11] == generate_way_key(0)[0:11]
    assert list( json.loads(rdw.get(generate_way_key(0))).keys()) == ["type","properties","geometry"] 
    assert isinstance( json.loads(rdw.get(generate_way_key(0)))["properties"]["sol"], int) == True
    assert isinstance( json.loads(rdw.get(generate_way_key(0)))["properties"]["easting"], float) == True
    assert isinstance( json.loads(rdw.get(generate_way_key(0)))["properties"]["Note"], str) == True

# TRAVERSE DATABASE TESTS
def test_rdatabase_trav():
    assert len(rdt.keys())>0
    assert list(rdt.keys())[0].decode('utf-8')[0:11] == generate_trav_key(0)[0:11]
    assert list( json.loads(rdt.get(generate_trav_key(0))).keys()) == ["type","properties","geometry"] 
    assert isinstance( json.loads(rdt.get(generate_trav_key(0)))["properties"]["length"], float) == True
    assert list( json.loads(rdt.get(generate_trav_key(0)))["geometry"].keys()) == ["type","coordinates"] 
    assert isinstance( json.loads(rdt.get(generate_trav_key(0)))["geometry"]["coordinates"], list) == True    
    assert isinstance( json.loads(rdt.get(generate_trav_key(0)))["geometry"]["coordinates"][0][0], float) == True

