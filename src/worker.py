from jobs import q,rd, update_job_status, get_job_by_id
from time import sleep
import matplotlib.pyplot as plt

@q.worker
def execute_ploting_job(jid):
    
    update_job_status(jid, 'in progress')
    job = get_job_by_id(jid)

    # NEEDS TO BE FIXED
    x_values_to_plot = []
    y_values_to_plot = []
    # for key in raw_data.keys():       # raw_data.keys() is a client to the raw data stored in redis
    #     if ( int(job['start']) <= key['date'] <= int(job['end']) ):
    #         x_values_to_plot.append(key['interesting_property_1'])
    #         y_values_to_plot.append(key['interesting_property_2'])

    plt.scatter(x_values_to_plot, y_values_to_plot)
    plt.savefig('/output_image.png')
    with open('/output_image.png', 'rb') as f:
        img = f.read()

    # PLACE THE IMAGE BYTES KEY ON THE JOB REQUEST ITSELF
    rd.hset('job.{}'.format(jid), 'image', img)

    update_job_status(jid, 'complete')
    return