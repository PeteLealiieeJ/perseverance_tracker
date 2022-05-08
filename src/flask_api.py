# STATUS: IN PROGRESS
####################################################################################################
# IMPORTANT NOTES
'''
CURRENTLY DATA IS BEING STORED ON THE REDIS SERVER WITH THE FOLLOWING PARAMETERS:
REDIS KEY STRING FORMAT -> dataset_{ii} [where {ii} is the index at which the list element was uploaded]
RETURN FORMAT -> json holding a single element in the features list of the encompassing json (sol indexed datasets)
'''
####################################################################################################

# FLASKS LIBRARIES
from flask import Flask, request, jsonify, send_file
#LIBRARY USED TO PULL JSON FROM NASA SOURCE
import requests 
# JSON LIBRARIES
import json
# LOCAL 
from jobs import rdw,rdt,rdj
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
def generate_way_key(id):
  return 'way_dataset.{}'.format(id)

def generate_trav_key(id):
  return 'trav_dataset.{}'.format(id)


def xyser_by_waykeys(xkey,ykey):
    # RUN THROUGH KEYS AND APPEND TO DATA LIST
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'
    xset = []
    yset = []
    for ii in range(len(rdw.keys())):
        element = rdw.get(generate_way_key(ii))
        if not element is None:
            xset.append(json.loads(element)['properties'][xkey])
            yset.append(json.loads(element)['properties'][ykey])
    xydict = {'xser': xset, 'yser': yset}
    return xydict
####################################################################################################


# FLASK ROUTE FUNCTIONS 
####################################################################################################


# @app.route('/jobs', methods=['POST'])
# def jobs_api():
#     """
#     API route for creating a new job to do some analysis. This route accepts a JSON payload
#     describing the job to be created.
#     """
#     timeser = []
#     posser = []
#     try:
#         # get start and end locations
#         job = request.get_json(force=True)
#     except Exception as e:
#         return True, json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})
#     return json.dumps(jobs.add_job( timeser, posser, job['start'], job['end']))


@app.route('/download/<jid>', methods=['GET'])
def download(jid):
    path = f'/app/{jid}.png'
    with open(path, 'wb') as f:
        f.write(rdj.hget(jid, 'image'))
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


### PRIMARY DATA ROUTES ###

# @app.route('/perseverance/sol')
# # Most recent waypoints sol identifier
# # sting

# @app.route('/perseverance/orientation')
# # All orientation data
# # json

@app.route('/perseverance/orientation/yaw')
def yaw_req():
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'

    serDataDict = xyser_by_waykeys('sol','yaw')
    try:
        # get start and end locations
        job = request.get_json(force=True)
    except Exception as e:
        return True, json.dumps({'status': "Error", 'message': 'Invalid JSON: {}.'.format(e)})
    return json.dumps(jobs.add_job( str(serDataDict['xser']), str(serDataDict['yser']), job['start'], job['end']))


### TEST FUNCTIONS WHICH REQUIRE ADDITIONAL WORK FOR FUNCTIONALITY

@app.route('/perseverance/orientation/pitch')
def pitch_req():
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'
    serDataDict = xyser_by_waykeys('sol','pitch')
    return(jsonify(serDataDict))

@app.route('/perseverance/orientation/roll')
def roll_req():
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'
    serDataDict = xyser_by_waykeys('sol','roll')
    return(jsonify(serDataDict))

# @app.route('/perseverance/position')
# # All position data
# # json

@app.route('/perseverance/position/longitude')
def lat_req():
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'
    serDataDict = xyser_by_waykeys('sol','lon')
    return(jsonify(serDataDict))


@app.route('/perseverance/position/latitude')
def lat_req():
    if(len(rdw.keys())==0):
        return 'Please use /load with POST route \n'
    serDataDict = xyser_by_waykeys('sol','lat')
    return(jsonify(serDataDict))

# @app.route('/perseverance/position/map')
# # Latitude and Longitude of Rover on map
# # job plot

# @app.route('/perseverance/stats/distance')
# # returns total distance travelled from traverse src 
# # string

# @app.route('/perseverance/stats/duration')
# # returns current sol of mission
# # string


####################################################################################################


### MAIN 
####################################################################################################
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')    
####################################################################################################