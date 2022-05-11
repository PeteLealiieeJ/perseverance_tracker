# PYTEST NON-CONTAINERIZED REQUIREMENT
import pytest, requests
from redis import StrictRedis
from typing import Type
import json
import sys, os
from time import sleep
from test_db import REDIS_TEST_IP, REDIS_TEST_PORT

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(f'{parentdir}/src')

from jobs import get_job_by_id,decode_byte_dict,generate_job_key

# LOAD DATA TO REDIS SERVICE
FPORT = 5015
BASEROUTE = f'http://localhost:{FPORT}'
requests.post(f'{BASEROUTE}/')

JOB_REDIS_DB = 2
rdj = StrictRedis(host=REDIS_TEST_IP, port=REDIS_TEST_PORT, db=JOB_REDIS_DB)


# WAYPOINT DATABASE TESTS
def test_rdatabase_job():
    """
    Tests to check data format passed to worker is correct
    """
    starti = 0
    endi = 400
    jidi = requests.post(f'{BASEROUTE}/perseverance/position/latitude',json={"start":str(starti),"end":str(endi)})
    jidi = jidi.replace('The job has entered the hotqueue with ID: \n','')
    jidi = jidi.replace(' \nCheck back at /download/<jid> \n','')
    jobdicti = decode_byte_dict(rdj.hgetall(generate_job_key(jidi)) )

    sleep(1)
    assert list(jobdicti.keys()) == ["pltopt","status","id","datakeys","end","start"]
    assert jobdicti["status"] == "complete"
    assert jobdicti["start"] == str(starti)
    assert jobdicti["end"] == str(endi)
    assert jobdicti["pltopt"] == "{\"title\": \"Perseverance: Rover Latitude v Time\", \"xlabel\": \"Time [sol]\", \"ylabel\": \"Latitude [deg]\"}"
    assert jobdicti["datakeys"] == "{\"type\": \"way\", \"xdata\": \"sol\", \"ydata\": \"lat\"}"

    return


def test_worker():
    """
    Tests the Misc plotting job and a direct position plotting job for creation and completion by worker
    """
    startmap = 0
    endmap = 400
    jidmap = requests.post(f'{BASEROUTE}/perseverance/position/map',json={"start":startmap,"end":endmap})
    jidmap = jidmap.replace('The job has entered the hotqueue with ID: \n','')
    jidmap = jidmap.replace(' \nCheck back at /download/<jid> \n','')
    jobdictmap = decode_byte_dict(rdj.hgetall(generate_job_key(jidmap)) )

    startmisc = 0
    endmisc = 400
    jidmisc = requests.post(f'{BASEROUTE}/jobs',json={"type":"way","xkey":"lon","ykey":"yaw","start":startmisc,"end":endmisc})
    jidmisc = jidmisc.replace('The job has entered the hotqueue with ID: \n','')
    jidmisc = jidmisc.replace(' \nCheck back at /download/<jid> \n','')
    jobdictmisc = decode_byte_dict(rdj.hgetall(generate_job_key(jidmisc)) )

    sleep(3)
    assert jobdictmap["status"] == "complete"
    assert jobdictmisc["status"] == "complete"

    return