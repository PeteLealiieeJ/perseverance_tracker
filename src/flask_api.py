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
from flask import Flask, request, jsonify
# REDIS LIBRARIES
import redis
#LIBRARY USED TO PULL JSON FROM NASA SOURCE
import requests 
# JSON LIBRARIES
import json

# CONSTANTS
####################################################################################################
### SOURCE DATA URL
DATA_SRC_URL = 'https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json'
### KUBE SERVICE IP
REDIS_SERVICE_IP = ''
####################################################################################################


# LIBRARY CONFIGURATIONS
####################################################################################################
### FLASK APPLICATION VARIABLES 
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

### REDIS DATABASE VARIABLES
rd = redis.Redis(host=REDIS_SERVICE_IP, port=6379, db=4)
####################################################################################################


# FILTERING AND INTERMEDIATE FUNCTIONS 
####################################################################################################

####################################################################################################


# FLASK ROUTE FUNCTIONS 
####################################################################################################
### LOADS PRIMARY BODY OF FLASK APPLICATION
@app.route('/data', methods=['POST'])
def load_data():
    """                                                                                                                                                                                              
    Called to update the perseverance data sets used for services 
    args:
        (none)                                                                                                                               
    returns:                                                                                                                                                                                         
        (str): Confirmation of Read                                                                                                                     
    """
    pulled_data = requests.get(url=DATA_SRC_URL).json()['features']
    for ii in range(len(pulled_data)):
        set_str = f'dataset_{ii}'
        rd.set( set_str, json.dumps(pulled_data[ii]) )
    return f'Data has been loaded from the Source URL below: \n URL: {DATA_URL} \n'


@app.route('/data', methods=['GET'])
def get_data():
    """                                                                                                                                                                                              
    Called to display the perseverance data sets with optional start arg         
    args:
        (none)                                                                                                                               
    returns:                                                                                                                                                                                         
        (json): Jsonified display of perseverance data                                                                                                                       
    """
    perseverance_data = []
    # CHECK REDIS FOR KEYS
    if(len(rd.keys())==0):
        return 'Please Load /data with POST route \n'

    # RUN THROUGH KEYS AND APPEND TO DATA LIST
    for ii in range(len(rd.keys())):
        set_str = f'dataset_{ii}'
        v = rd.get(set_str)
        if not v is None:
            perseverance_data.append(json.loads(v))

    # OPTIONAL START PARAMETER
    start = request.args.get('start', 0)
    if start:
        try:
            start = int(start)
        except ValueError:
            return "Invalid start parameter; start must be an integer \n"
    if (start+1)>len(rd.keys()):
        return "Start index is greater than the number of data sets \n"

    return jsonify(perseverance_data[start:])
####################################################################################################


### MAIN 
####################################################################################################
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')    
####################################################################################################