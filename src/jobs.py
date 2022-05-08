# REDIS LIBRARIES
from redis import StrictRedis
# QUEUING LIBRARIES
from hotqueue import HotQueue
# IDENTIFIERS 
import uuid 

# CONSTANTS
####################################################################################################
### KUBE SERVICE IP
REDIS_SERVICE_IP = ''
WAYDATA_REDIS_DB = 0
TRAVDATA_REDIS_DB = 1
JOB_REDIS_DB = 2
QUEUE_REDIS_DB = 3
####################################################################################################

# LIBRARY CONFIGURATIONS
####################################################################################################
rdw = StrictRedis(host=REDIS_SERVICE_IP, port=6379, db=WAYDATA_REDIS_DB)
rdt = StrictRedis(host=REDIS_SERVICE_IP, port=6379, db=TRAVDATA_REDIS_DB)
rdj = StrictRedis(host=REDIS_SERVICE_IP, port=6379, db=JOB_REDIS_DB)
q = HotQueue("queue", host=REDIS_SERVICE_IP, port=6379, db=QUEUE_REDIS_DB)
####################################################################################################

# FUNCTIONALITY 
####################################################################################################
def generate_jid():
    """
    Generate a pseudo-random identifier for a job.
    """
    return str(uuid.uuid4())


def generate_job_key(jid):
  """
  Generate the redis key from the job id to be used when storing, retrieving or updating
  a job in the database.
  """
  return 'job.{}'.format(jid)


def instantiate_job(jid, xdatastr, ydatastr, status, start, end):
    """
    Create the job object description as a python dictionary. Requires the job id, status,
    start and end parameters.
    """
    if type(jid) == str:
        return    {'id': jid,
                'xdata': xdatastr,
                'ydata': ydatastr,
                'status': status,
                'start': start,
                'end': end
                }
    return    {'id': jid.decode('utf-8'),
            'xdata': xdatastr.decode('utf-8'),
            'ydata': ydatastr.decode('utf-8'),
            'status': status.decode('utf-8'),
            'start': start.decode('utf-8'),
            'end': end.decode('utf-8')
            }


def save_job(job_key, job_dict):
    """Save a job object in the Redis database."""
    rdj.hset(job_key, mapping=job_dict)


def queue_job(jid):
    """Add a job to the redis queue."""
    q.put(jid)


def add_job(xdata, ydata, start, end, status="submitted"):
    """Add a job to the redis queue."""
    jid = generate_jid()
    job_dict = instantiate_job(jid, str(xdata), str(ydata), status, start, end)
    # update call to save_job:
    save_job(generate_job_key(jid), job_dict)
    # update call to queue_job:
    queue_job(jid)
    return job_dict


def decode_byte_dict(bdict):
    ddict = {}
    for key in bdict.keys():
        ddict[key.decode('utf-8')] = bdict[key].decode('utf-8')
    return ddict


def get_job_by_id(jid):
    """Save a job object in the Redis database."""
    return decode_byte_dict( rdj.hgetall(generate_job_key(jid)) )
    

def update_job_status(jid, status):
    """Update the status of job with job id `jid` to status `status`."""
    job = get_job_by_id(jid)
    if job:
        job['status'] = status
        save_job(generate_job_key(jid), job)
    else:
        raise Exception()
    return


####################################################################################################