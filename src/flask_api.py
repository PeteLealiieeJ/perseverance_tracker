# STATUS: IN PROGRESS
####################################################################################################

# FLASKS LIBRARIES
from flask import Flask, request, jsonify, send_file
#LIBRARY USED TO PULL JSON FROM NASA SOURCE
import requests 
# JSON LIBRARIES
import json
# LOCAL 
from jobs import rdw,rdt,rdj, generate_trav_key, generate_way_key, generate_job_key, decode_byte_dict
import jobs 

# CONSTANTS
####################################################################################################
### SOURCE DATA URL
# ORGANIZED INDEXED BY APPROPRIATE SOL SPACING (SOL INDEXED)
WAYPOINT_SRC_URL = 'https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json'
# INTERMEDIATE TRAVERSAL DATA FOR MAP PLOTTING (NOT SOL INDEXED)
TRAVERSE_SRC_URL = 'https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_traverse.json'
####################################################################################################


# LIBRARY CONFIGURATIONS
####################################################################################################
### FLASK APPLICATION VARIABLES 
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
####################################################################################################


# FILTERING AND INTERMEDIATE FUNCTIONS 
####################################################################################################
def ser_by_waykeys(key):
    # RUN THROUGH KEYS AND APPEND TO DATA LIST
    if(len(rdw.keys())==0):
        return []
    dset = []
    for ii in range(len(rdw.keys())):
        element = rdw.get(generate_way_key(ii))
        if not element is None:
            dset.append(json.loads(element)['properties'][key])
    return dset


def dlist_by_waykeys(keylist):
    # FILTERS KEYS OF SRC DATA
    if(len(rdw.keys())==0):
        return []
    dictlist = []
    for ii in range(len(rdw.keys())):
        element = rdw.get(generate_way_key(ii))
        if not element is None:
            ddict = {}
            for key in keylist:
                ddict[key] = json.loads(element)['properties'][key]
            dictlist.append(ddict)
    return dictlist


def generate_data_key(typei,xdatai,ydatai):
    return json.dumps({'type':typei,'xdata':xdatai,'ydata':ydatai})

def generate_plot_key(titlei,xlabeli,ylabeli):
    return json.dumps({'title':titlei,'xlabel':xlabeli,'ylabel':ylabeli})
####################################################################################################


# FLASK ROUTE FUNCTIONS 
####################################################################################################

# INFORMATIONAL CARDS 
### USAGE INFOFORMATION FUNCTION
@app.route('/', methods=['GET'])
def usage_info():
    """                                                                                                                                                                                              
    Called to print usage information for API
        (none)                                                                                                                                  
    returns:                                                                                                                                                                                         
        (str) Formatted Usage Information for users                                                                                                                            
    """
    usage_tab = [
        ['### Peseverance Tracker ###', ''],
        ['',''],
        ['Informational and Management Routes:', ''],
        ['/', '(GET) Print Route Information'],
        ['/load', '(POST) Loads/Overwrites Data from Perseverance sources'  ],
    ]

    job_tab = [
        ['Plotting Job Routes:', ''],
        ['/download/<jid>', '(GET) Get the Job Image from Routes Below'],        
        ['/jobs', '(POST) Post Job for Misc Plot'],
        ['/perseverance/orientation/yaw', '(POST) Post job for "Yaw v Sol" Plot'],
        ['/perseverance/orientation/pitch', '(POST) Post job for "Pitch v Sol" Plot'],
        ['/perseverance/orientation/roll', '(POST) Post job for "Roll v Sol" Plot'],
        ['/perseverance/position/longitude', '(POST) Post job for "Longitude v Sol" Plot'],
        ['/perseverance/position/latitude', '(POST) Post job for "Latitude v Sol" Plot'],
        ['/perseverance/position/map', '(POST) Post job for "Latitude v Longitude" Plot'],
    ]
    
    general_tab = [
        ['General Rover State Routes:',''],
        ['/perseverance','(GET) List all Waypoint Data'],
        ['/perseverance/sol','(GET) List Most Current Sol in Data'],
        ['/perseverance/orientation','(GET) List All Orientation Data w Sol-Idx'],
        ['/perseverance/position','(GET) List All Positioning Data w Sol-Idx'],

    ]

    spacer_tab = [
        ['',''],
    ]

    full_tab = usage_tab + spacer_tab + job_tab + spacer_tab + general_tab + spacer_tab
    usage_str = '\n'
    for x in full_tab:
        usage_str += ( "    {: <70} {: <70} ".format(*x) + '\n' )
    return usage_str



# ROUTE FOR REQUESTING PLOTTING JOB
@app.route('/jobs', methods=['POST'])
def jobs_api():
    """ 
    MISCELLANEOUS JOBS FOR PLOTS KEYS VS OTHERS
    """
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'
    try:
        # GET START AND END LOCATIONS
        req = request.get_json(force=True)
    except Exception as e:
        return jsonify({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})  
    # ONE OF KEYS
    xkey = req['xkey']
    ykey = req['ykey']
    # DBTYPE = WAY OR TRAV
    dbtype = req['type']
    title = f'Perseverance: Rover {ykey} v {xkey}'
    retjid = jobs.add_job(  generate_data_key(dbtype,xkey,ykey), 
                            generate_plot_key(title,xkey,ykey), 
                            req['start'], 
                            req['end'] ) 
    return f'The job has entered the hotqueue with ID: \n{retjid} \nCheck back at /download/<jid> \n '


@app.route('/jobs/list', methods=['GET'])
def jobs_list():
    jobs_list = []
    for key in list(rdj.keys()):
        v = rdj.get(key)
        if not v is None:
            jobs_list.append(decode_byte_dict(v))
    return jsonify(jobs_list)

# DOWNLOADING ROUTE
@app.route('/download/<jid>', methods=['GET'])
def download(jid):
    path = f'/app/{jid}.png'
    with open(path, 'wb') as f:
        f.write(rdj.hget(generate_job_key(jid), 'image'))
    return send_file(path, mimetype='image/png', as_attachment=True)


### LOADS PRIMARY BODY OF FLASK APPLICATION
@app.route('/load', methods=['POST'])
def load_data():
    """                                                                                                                                                                                              
    Called to update the perseverance data sets used for services 
    args:
        (none)                                                                                                                               
    returns:                                                                                                                                                                                         
        (str): Confirmation of Read                                                                                                                     
    """
    pulled_way_data = requests.get(url=WAYPOINT_SRC_URL).json()['features']
    for ii in range(len( pulled_way_data)):
        rdw.set( generate_way_key(ii), json.dumps( pulled_way_data[ii]) )

    pulled_trav_data = requests.get(url=TRAVERSE_SRC_URL).json()['features']
    for ii in range(len( pulled_trav_data)):
        rdt.set( generate_trav_key(ii), json.dumps( pulled_trav_data[ii]) )

    return f'Data has been loaded from the Source URLs below: \n WAYPOINTS: {WAYPOINT_SRC_URL} \n TRAVERSAL: {TRAVERSE_SRC_URL} \n '


### RETURNS ALL RELEVANT WAYPOINT SOURCES DATA
@app.route('/perseverance', methods=['GET'])
def get_data():
    """                                                                                                                                                                                              
    Called to display the perseverance waypoint data sets with optional start arg         
    args:
        (opt) start: Start index for displaying data                                                                                                                               
    returns:                                                                                                                                                                                         
        (json): Jsonified display of perseverance data                                                                                                                       
    """
    perseverance_data = []
    # CHECK REDIS FOR KEYS
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'

    # RUN THROUGH KEYS AND APPEND TO DATA LIST
    for ii in range(len(rdw.keys())):
        v = rdw.get(generate_way_key(ii))
        if not v is None:
            perseverance_data.append(json.loads(v))

    # OPTIONAL START PARAMETER
    start = request.args.get('start', 0)
    if start:
        try:
            start = int(start)
        except ValueError:
            return "Invalid start parameter; start must be an integer \n"
    if (start+1)>len(rdw.keys()):
        return "Start index is greater than the number of data sets \n"

    return jsonify(perseverance_data[start:])


### PRIMARY DATA ROUTES (USES WAYPOINT SRC URL) ###

@app.route('/perseverance/sol', methods=['GET'])
def sol_req():
    allSol = ser_by_waykeys('sol')
    return f'Most recent data waypoint is at Sol-{max(allSol)}'


@app.route('/perseverance/orientation', methods=['GET'])
def orientation_req():
    return jsonify( dlist_by_waykeys(['sol','yaw_rad','pitch','roll']) )


@app.route('/perseverance/orientation/yaw', methods=['POST'])
def yaw_req():
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'
    try:
        # GET START AND END LOCATIONS
        req = request.get_json(force=True)
    except Exception as e:
        return jsonify({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})  
    retjid = jobs.add_job(  generate_data_key('way','sol','yaw_rad'), 
                            generate_plot_key('Perseverance: Rover Yaw v Time','Time [sol]','Yaw [rads]'), 
                            req['start'], 
                            req['end'] ) 
    return f'The job has entered the hotqueue with ID: \n{retjid} \nCheck back at /download/<jid> \n '


@app.route('/perseverance/orientation/pitch', methods=['POST'])
def pitch_req():
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'
    try:
        # GET START AND END LOCATIONS
        req = request.get_json(force=True)
    except Exception as e:
        return jsonify({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})  
    retjid = jobs.add_job(  generate_data_key('way','sol','pitch'), 
                            generate_plot_key('Perseverance: Rover Pitch v Time','Time [sol]','Pitch [rads]'), 
                            req['start'], 
                            req['end'] ) 
    return f'The job has entered the hotqueue with ID: \n{retjid} \nCheck back at /download/<jid> \n '


@app.route('/perseverance/orientation/roll', methods=['POST'])
def roll_req():
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'
    try:
        # GET START AND END LOCATIONS
        req = request.get_json(force=True)
    except Exception as e:
        return jsonify({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})  
    retjid = jobs.add_job(  generate_data_key('way','sol','roll'), 
                            generate_plot_key('Perseverance: Rover Roll v Time','Time [sol]','Roll [rads]'), 
                            req['start'], 
                            req['end'] ) 
    return f'The job has entered the hotqueue with ID: \n{retjid} \nCheck back at /download/<jid> \n '


@app.route('/perseverance/position', methods=['GET'])
def position_req():
    return jsonify( dlist_by_waykeys(['sol','lon','lat']) )


@app.route('/perseverance/position/longitude', methods=['POST'])
def lon_req():
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'
    try:
        # GET START AND END LOCATIONS
        req = request.get_json(force=True)
    except Exception as e:
        return jsonify({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})  
    retjid = jobs.add_job(  generate_data_key('way','sol','lon'), 
                            generate_plot_key('Perseverance: Rover Longitude v Time','Time [sol]','Longitude [deg]'), 
                            req['start'], 
                            req['end'] ) 
    return f'The job has entered the hotqueue with ID: \n{retjid} \nCheck back at /download/<jid> \n '


@app.route('/perseverance/position/latitude', methods=['POST'])
def lat_req():
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'
    try:
        # GET START AND END LOCATIONS
        req = request.get_json(force=True)
    except Exception as e:
        return jsonify({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})  
    retjid = jobs.add_job(  generate_data_key('way','sol','lat'), 
                            generate_plot_key('Perseverance: Rover Latitude v Time','Time [sol]','Latitude [deg]'), 
                            req['start'], 
                            req['end'] ) 
    return f'The job has entered the hotqueue with ID: \n{retjid} \nCheck back at /download/<jid> \n '


@app.route('/perseverance/position/map', methods=['POST'])
def map_req():
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'
    try:
        # GET START AND END LOCATIONS
        req = request.get_json(force=True)
    except Exception as e:
        return jsonify({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})  
    retjid = jobs.add_job(  generate_data_key('way','lat','lon'), 
                            generate_plot_key('Perseverance: Rover Longitude v Latitude','Latitude [deg]','Longitude [deg]'), 
                            req['start'], 
                            req['end'] ) 
    return f'The job has entered the hotqueue with ID: \n{retjid} \nCheck back at /download/<jid> \n '


### SECONDARY DATA ROUTES (USES TRAVERSE SRC URL) ###
# @app.route('/perseverance/stats/distance')
# # returns total distance travelled from traverse src 
# # string


####################################################################################################


### MAIN 
####################################################################################################
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')    
####################################################################################################
