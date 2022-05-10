# PYTEST NON-CONTAINERIZED REQUIREMENT
import pytest, requests
from redis import StrictRedis
from typing import Type
import json
import sys, os

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(f'{parentdir}/src')

from jobs import generate_job_key

FPORT = 5015
BASEROUTE = f'http://localhost:{FPORT}'
requests.post(f'{BASEROUTE}/')

# MUST BE CHANGED EVERYTIME CONTAINER ISN'T SET
REDIS_TEST_IP = '172.17.0.17'
REDIS_TEST_PORT = 6379

JOB_REDIS_DB = 2
rdj = StrictRedis(host=REDIS_TEST_IP, port=REDIS_TEST_PORT, db=JOB_REDIS_DB)


# WAYPOINT DATABASE TESTS
def test_rdatabase_job():
    return


def test_worker():
    return