from jobs import q,rdj,rdw, rdt, generate_way_key, generate_job_key, generate_trav_key, update_job_status, get_job_by_id
from time import sleep
import matplotlib.pyplot as plt
import json


def xyser_by_waykeys(xkey,ykey):
    # RUN THROUGH KEYS AND APPEND TO DATA LIST
    if(len(rdw.keys())==0):
        return {}
    xset = []
    yset = []
    for ii in range(len(rdw.keys())):
        element = rdw.get(generate_way_key(ii))
        if not element is None:
            xset.append(json.loads(element)['properties'][xkey])
            yset.append(json.loads(element)['properties'][ykey])
    xydict = {'xser': xset, 'yser': yset}
    return xydict


def xyser_by_waykeys(xkey,ykey):
    # RUN THROUGH KEYS AND APPEND TO DATA LIST
    if(len(rdt.keys())==0):
        return {}
    xset = []
    yset = []
    for ii in range(len(rdt.keys())):
        element = rdt.get(generate_way_key(ii))
        if not element is None:
            xset.append(json.loads(element)['properties'][xkey])
            yset.append(json.loads(element)['properties'][ykey])
    xydict = {'xser': xset, 'yser': yset}
    return xydict


@q.worker
def execute_ploting_job(jid):
    update_job_status(jid, 'in progress')
    job = get_job_by_id(jid)
    dtype = job['datakeys']['type']
    if dtype == 'way':
        allData = xyser_by_waykeys(job['datakeys']['xdata'], job['datakeys']['ydata'])
    else:
        allData = xyser_by_waykeys(job['datakeys']['xdata'], job['datakeys']['ydata'])
    allX = allData['xser']
    allY = allData['yser']
    start = int(job['start'])
    end = int(job['end'])

    # NEEDS TO BE FIXED
    x_values_to_plot = []
    y_values_to_plot = []

    for ii in range(len(allX)):  
        if ( start <= allX[ii] <= end ):
            x_values_to_plot.append(allX[ii])
            y_values_to_plot.append(allY[ii])

    plt.scatter(x_values_to_plot, y_values_to_plot)
    # CREATES STORAGE PROBLEM I DONT FEEL LIKE ADDRESSING
    plt.savefig('/output_image.png')
    with open('/output_image.png', 'rb') as f:
        img = f.read()
    # PLACE THE IMAGE BYTES KEY ON THE JOB REQUEST ITSELF
    rdj.hset(generate_job_key(jid), 'image', img)
    update_job_status(jid, 'complete')
    return