#
# Perseverance Tracker - Understanding the Martian Rover 
This repository contains an API which tracks the Perseverance rover's traversal across the Martian surface, and provides data which is useful for understanding the Perseverance Rovers performance and state during the duration of its time on Mars. This repository contains the components and instructions necessary to deploy this API in an Image (with Docker) and on Kubernetes, so that the user can receive and visualize data from the rover with plots and responses from the API.

Firstly, the source data used for this API comes from NASA and can be found in the two links below. (Note that the repo uses only the Waypoint dataset; However, the traversal dataset is also stored on Redis volume for possible future use to make more accurate mapping plots)
- [Waypoint](https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_waypoints.json)
- [Traverse](https://mars.nasa.gov/mmgis-maps/M20/Layers/json/M20_traverse.json)

The Waypoint data is formatted as a json dictionary with a type and name identifier and (most applicably) a features list which provide important state and performance data indexed by sol-time. The json is formatted as seen below (note that we only provide a single element from the "features" list due to the length of data)

    {
        "type": "FeatureCollection",
        "name": "M20_Rover_Localizations_tosol0402",
        "features": [
        { 
            "type": "Feature", 
            "properties": { 
                "RMC": "3_0", 
                "site": 3,
                "drive": 0, 
                "sol": 13, 
                "SCLK_START": 0.0, 
                "SCLK_END": 0.0, 
                "easting": 4354494.086, 
                "northing": 1093299.695, 
                "elev_geoid": -2569.91, 
                "elev_radii": -4253.47, 
                "radius": 3391936.53, 
                "lon": 77.45088572, 
                "lat": 18.44462715, 
                "roll": -1.1817, 
                "pitch": -0.0251, 
                "yaw": 130.8816, 
                "yaw_rad": 2.2843, 
                "tilt": 1.18, 
                "dist_m": 0.0, 
                "dist_total": 0.0,
                "dist_km": 0.0, 
                "dist_mi": 0.0, 
                "final": "y", 
                "Note": "Site increment, no motion." 
            }, 
            "geometry": { 
                "type": "Point", 
                "coordinates": [ 77.450885720000031, 18.444627149999974, -2569.909999999999854 ] } 
        },
        …
        ]
    }

#
# Requirements for Local Use and Testing 
The following packages are required for direct use and are installed during container docker containerization (except for pytest which is only necessary for functionality testing)

1. Flask 
2. requests 
3. redis 
4. hotqueue 
5. tornado
6. matplotlib 
7. pytest

Each of the above python <package\> s can be installed locally with pip via

    pip install --user <package>

It is best that you install these packages they are listed to avoid unforeseen issues. (users should install tornado before matlibplot to avoid recent issues experienced with python3 dependencies) 

#
# Explanation of Functionality

The API, flask_api.py, itself is a python script which interacts with an assortment of databases and a worker - all which are deployed in three methods: directly, in container, and in Kubernetes. This API is dependent on Flask, a microweb framework used to develop microservices which make up REST APIs (discussed in earlier section). To add routes to be found by external clients of the service, we utilize decorators to a flask variable app. The functionality of these URL routes (employed by the decorators) are fulfilled with various pythons functions to filter the source data and by queuing and queue fulfillment via the worker script. For context, the request package is used to pull and update the source data from the NASA source via the web. The redis package is used to communicate with a database storage so that the API can store the source data sets and queued jobs in a reliable and persistent method. Finally, the hotqueue package is used for sending jobs requested by user to a queue which can work on these jobs in order of request without redundancy and erroneous behavior. The worker (worker.py) is an important component for assisting the API with fulfilling jobs queued by the base API (flask_api.py). The worker utilizes the hotqueue python package to decorate a redis connection variable, q, so that it checks the queue consistently for new jobs from the API. The worker reads the queue and utilizes its functionality to plot job requests one at a time. This is a task queue system in which the flask API is a “producer” which writes a job message to a queue that describe work to be done and the worker script is a “consumer” which receives the message and does the work. This system is important so that multiple “consumers” (API clients) can make messages to the “producer” workers which processes ALL their messages without duplication.

#
# Starting API with Docker Containers
The functionality of this repository can be containerized with docker via the dockerfiles and docker-compose file located in the [docker folder](./docker/) of this repository. The simpliest method of creating and running the containers of this repository is to utilize the docker-compose file. We can start up the api, worker and redis server via the following command:

    [P-Tracker/docker]$ docker-compose -p <namespace> up -d

from here the IPAdress of the application server is usually the localhost. From this point you can access all routes on the 5015 port of the localhost. See all routes in the **Communicating with perseverance-tracker API** section at the bottom of this README. When finished, all of the images can be spun down with the following command:

    [P-Tracker/docker]$ docker-compose -p <namespace> down

Alternatively, one could build and run the images with the following commands:

    [P-Tracker]$ docker build -t ${NSPACE}/${APP}-wrk:${VER} -f docker/Dockerfile.wrk .
    [P-Tracker]$ docker build -t ${NSPACE}/${APP}-api:${VER} -f docker/Dockerfile.api .
    [P-Tracker]$ docker run --name ${NSPACE}-db -p ${RPORT}:6379 -d  -u ${UID}:${GID} -v ${PWD}/data/:/data redis:6 --save 1 1
    [P-Tracker]$ docker run --name ${NSPACE}-wrk --env REDIS_IP=$$(docker inspect ${NSPACE}-db | grep \"IPAddress\" | head -n1 | awk -F\" '{print $$4}') -d ${NSPACE}/${APP}-wrk:${VER} 
    [P-Tracker]$ docker run --name ${NSPACE}-api --env REDIS_IP=$$(docker inspect ${NSPACE}-db | grep \"IPAddress\" | head -n1 | awk -F\" '{print $$4}') -p ${FPORT}:5000 -d ${NSPACE}/${APP}-api:${VER} 


(i.e. for isp users)

    [P-Tracker]$ docker build -t petelealiieej/perseverance-tracker-wrk:${VER} -f docker/Dockerfile.wrk .
    [P-Tracker]$ docker build -t petelealiieej/perseverance-tracker-api:${VER} -f docker/Dockerfile.api .
    [P-Tracker]$ docker run --name petelealiieej-db -p 6415:6379 -d  -u ${UID}:${GID} -v ${PWD}/data/:/data redis:6 --save 1 1
    [P-Tracker]$ docker run --name petelealiieej-wrk --env REDIS_IP=$$(docker inspect petelealiieej-db | grep \"IPAddress\" | head -n1 | awk -F\" '{print $$4}') -d petelealiieej/perseverance-tracker-wrk:0.1
    [P-Tracker]$ docker run --name petelealiieej-api --env REDIS_IP=$$(docker inspect petelealiieej-db | grep \"IPAddress\" | head -n1 | awk -F\" '{print $$4}') -p 5015:5000 -d petelealiieej/perseverance-tracker-api:0.1

These steps are automated with the following Make command:
    
    []$ make run-all

and can be spun down wit the following:

    []$ make clean-all

Again, from here the IPAdress of the application server is usually the localhost. From this point you can access all routes on the 5015 port of the localhost. See all routes in the **Communicating with perseverance-tracker API** section at the bottom of this README.

#
# Integration Testing Application, Worker, Database
Integration tests are done via pytest and test the functionality of the flask application, worker and database in the following files:
- [test_db.py](./test/test_db.py)
- [test_flask_api.py](./test/test_flask_api.py)
- [test_worker.py](./test/test_worker.py)

Firstly, the test_db.py file contains functions for testing the database. This file includes functions to test both the waypoint and traverse databases containing the traverse and waypoint data, respectively . These test include checking that all the redis keys match the formatting created with the respective *generate_way_key()* and *generate_trav_key()* functions, and checking that the data stored in the database have the appropriate dictionary keys and value types.

Next, the test_flask_api.py file contains functions for testing the non-job-related routes of the flask application. This file includes functions to test the (GET) routes and load (POST) route - and the other (POST) routes which interact with the worker script are reserved for the test_worker.py script. These tests include checking that all the flask routes return appropriately formatted responses, successful response codes, and appropriately types from response content, lists, and dictionaries.

Finally, the test_worker.py file contains functions for testing the job-related routes of the flask application. This file includes functions to test all job (POST) routes and the download (GET) routes - and the other (POST) routes which do not interact with the worker script are reserved for the test_flask_api.py script. These tests include checking that all the flask routes return appropriately formatted responses, successful response codes, and appropriately types from response content, lists, and dictionaries. 

All of the above test are executed utilizing pytest and can be initiated after spinning up the services and containers. One may also need to update the FPORT, BASEROUTE, REDIS_TEST_IP and REDIS_TEST_PORT variables in test files to their own in order to run the database test successfully.

    [P-Tracker]$ make run-all
    [P-Tracker]$ make redis-ip # Gets Redis IP for replacement in test_db.py
    [P-Tracker]$ pytest

Successful test should give the following response which shows that all tests were successful:

    ======================================================================================== test session starts =========================================================================================
    platform linux -- Python 3.6.8, pytest-7.0.1, pluggy-1.0.0
    rootdir: /home/pete0100/perseverance_tracker/test
    collected 8 items                                                                                                                                                                                    

    test_db.py ..                                                                                                                                                                                  [ 25%]
    test_flask_api.py ....                                                                                                                                                                         [ 75%]
    test_worker.py ..                                                                                                                                                                              [100%]

    ========================================================================================= 8 passed in 0.33s ==========================================================================================

If the test are not successful then post the issue to the github repository page.


#
# Kubernetes - PVC and Deployment & Services for Redis Server
To deploy Redis onto a Kubernete system we have proved the following yaml files in the [kubernetes db folder](./kubernetes/db) to command a Kubernete system:

- ptracker-db-pvc.yml
- ptracker-db-deployment.yml
- ptracker-db-service.yml

The persistent volume claims (pvc) is required to create the allocations needed to start the redis server so we will apply this yaml first:

    [../kubernetes/db]$ kubectl apply -f ptracker-db-pvc.yml

A creation confirmation message will be issued if all is well. Note that this yaml file makes the following allocations on the Kubernete system: the yaml file claims 1 GB of storage, for read and write access, with a NFS storage system under the base name  "mptracker-petenick-data"

Next, start the redis deployment with the following command:

    [../kubernetes/db]$ kubectl apply -f ptracker-db-deployment.yml

A creation confirmation message will be issued if all is well. This deployment starts and maintains 1 pod which is running the redis:6 image pulled down from dockerhub on the mounted path "/data" and under the name "ptracker-petenick-redis." You can check that the deployments are running with the following command:

    [kube]$ kubectl get deployments 

this should show the following at this point:

    NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
    ptracker-petenick-redis   1/1     1            1           41h

In order to maintain a persistent IP connection identifier we deploy services for the redis deployment with the following command

    [../kubernetes/db]$ kubectl apply -f ptracker-db-service.yml

This service matches to the redis deployment and exposes (and targets exposure of) services onto the 6379 port of the service's CLUSTER-IP address. To get the CLUSTER-IP address of service we can run the following:

    [kube]$ kubectl get services 

which will output something similar to the following:

    NAME                                  TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
    ptracker-petenick-redis-service   ClusterIP   10.96.245.190   <none>        6379/TCP   41h

record the IP address you get from the get-services command for use in the flask deployment section

All of these steps in this section can be complete with the following command:

    [.../kubernetes]$ kubectrl apply -f kubernetes/db/

#
# Kubernetes - Updating Jobs.py and Pushing New Images
After getting the clusterIP of the redis service, open the [job.py](src/jobs.py) file provided and change the present 

    REDIS_SERVICE_IP = "some string"

 in line 13 to your personal cluster ip found in the previous section. Then build the image per the steps below for your own docker image for the flask application

To build and push an image of the application and worker via docker you can run the following command:

    [P-Tracker]$ docker build -t ${NSPACE}/${APP}-wrk:${VER} -f docker/Dockerfile.wrk .
    [P-Tracker]$ docker build -t ${NSPACE}/${APP}-api:${VER} -f docker/Dockerfile.api .
    [P-Tracker]$ docker push ${NSPACE}/${APP}-wrk:${VER}
    [P-Tracker]$ docker push ${NSPACE}/${APP}-api:${VER}


(i.e. for isp users)

    [P-Tracker]$ docker build -t petelealiieej/perseverance-tracker-wrk:0.1 -f docker/Dockerfile.wrk .
    [P-Tracker]$ docker build -t petelealiieej/perseverance-tracker-api:0.1 -f docker/Dockerfile.api .
    [P-Tracker]$ docker push petelealiieej/perseverance-tracker-wrk:0.1 
    [P-Tracker]$ docker push petelealiieej/perseverance-tracker-api:0.1 

Alternatively, this command is made simpler with the Makefile - you may only need to change the NAME parameter value (Note that this command also pushes the docker image up to dockerhub so it may fail for some):

    [P-Tracker]$ make build-all
    [P-Tracker]$ make push-all

Because the image is already built and exist on Dockerhub, the Kubernete flask deployment yaml file is set to pull my own image and redis IP when deploying the flask application onto the Kubernete system, so be sure to change the file per the instructions in the next section.

#
# Kubernetes - Deployment & Services for Flask Application and Worker
To deploy the api and worker onto a Kubernete system we have proved the following yaml files in the [kubernetes test folder](./kubernetes/test) to command a Kubernete system:

- ptracker-api-deployment.yml
- ptracker-api-service.yml

Firstly, we will need to change the "ptracker-api-deployment.yml" so that the flask deployment will use YOUR image and redis IP address when deploying onto the Kubernete system. Open the "ptracker-api-deployment.yml" and change the spec.template.spec.containers.image value to your pushed docker image from the section before.

Next deploy the flask application and worker onto the Kubernete system with the following command:

    [.../kubernetes/prod]$ kubectl apply -f ptracker-api-deployment.yml
    [.../kubernetes/prod]$ kubectl apply -f ptracker-wrk-deployment.yml

This command deploys 2 pods of the flask application image onto your Kubernete system under the base name "meteoritelanding-pete0100-flask-test." You can check that the deployments are running with the following command:

    []$ kubectl get deployments 

this should show the following at this point:

    NAME                                   READY   UP-TO-DATE   AVAILABLE   AGE
    ptracker-petenick-wrk     2/2     2            2           40h
    ptracker-petenick-flask   2/2     2            2           40h
    ptracker-petenick-redis   1/1     1            1           41h

In order to maintain a persistent IP connection identifier we deploy services for the flask deployment with the following command

    [.../kubernetes/prod]$ kubectl apply -f ptracker-api-service.yml

This service matches to the flask deployment and exposes (and targets exposure of) services onto the 5000 port of the service's IP address. To get the CLUSTER-IP address of service we can run the following:

    [kube]$ kubectl get services 

which will output something similar to the following:

    NAME                                  TYPE        CLUSTER-IP      EXTERNAL-IP   PORT(S)    AGE
    ptracker-petenick-flask-service   ClusterIP   10.108.76.215   <none>        5000/TCP   40h
    ptracker-petenick-redis-service   ClusterIP   10.96.245.190   <none>        6379/TCP   41h

Your unique Cluster IP address for the flask-service is what will be used to communicate with the flask API and is what will be referred to as your <flask-service-CLUSTERIP\>. 

All of these steps in this section can be complete with the following command:

    [.../kubernetes]$ kubectrl apply -f kubernetes/prod/

#
# Kubernetes - Communicating Through Python Deployment
Next we must deploy another python-debug pod in the same namespace to communicate with the flask service on the kubernete. We first deploy that service with the following command: 

    [.../kubernetes/prod]$ kubectl apply -f deployment-python-debug.yml

Next we check the python-debug pods identifier with the following command:

    [kube]$ kubectl get pods

which will output the something similar to the following:

    NAME                                                    READY   STATUS    RESTARTS   AGE
    ...
    py-debug-deployment-5dfcf7bdd9-m6zvs                    1/1     Running   0          41h

Then we enter the pod with the following command to enter the pod in the "python-debug#" terminal/environment:

    [kube]$ kubectl exec -it <python-pod-id> -- /bin/bash

(i.e. for isp users)

    [kube]$ kubectl exec -it py-debug-deployment-5dfcf7bdd9-m6zvs -- /bin/bash


After deploying the flask and redis servers via the instructions in the section and entering the python debug deployment, before you can first load (and update) the data stored on the server via the command below utilizing curl:

    [python-debug#] curl <flask-service-CLUSTERIP>:<flask-port>/<route>

(i.e. for isp users)

    [python-debug#] curl <flask-service-CLUSTERIP>:5000/load -X POST

The next section will go into more specifics on the routes available to users. 

# Communicating with perseverance-tracker API
The informational route describes the communication routes with the api best. We can use the informational route and visualize the routes of the api with the  following command. Note that if the user is running with the images, <IPaddress\> is usually the localhost. If using the kubernetes deployment, the user must be in a python deployment and the <IPaddress\> will be the IPCluster (in the previous section <flask-service-CLUSTERIP\>).

    []$ curl <IPaddress>:5015

The above command will present the following informational:

     ### Peseverance Tracker ###                                                                                                                   
                                                                                                                                                  
    Informational and Management Routes:                                                                                                          
    /help                                                                  (GET) Print Route Information                                          
    /load                                                                  (POST) Loads/Overwrites Data from Perseverance sources                 
                                                                                                                                                  
    Plotting Job Routes:                                                                                                                          
    /download/<jid>                                                        (GET) Get the Job Image from Routes Below                              
    /jobs                                                                  (POST) Post Job for Misc Plot                                          
    /jobs/list                                                             (GET) List all jobs and their status                                   
    /perseverance/orientation/yaw                                          (POST) Post job for "Yaw v Sol" Plot                                   
    /perseverance/orientation/pitch                                        (POST) Post job for "Pitch v Sol" Plot                                 
    /perseverance/orientation/roll                                         (POST) Post job for "Roll v Sol" Plot                                  
    /perseverance/position/longitude                                       (POST) Post job for "Longitude v Sol" Plot                             
    /perseverance/position/latitude                                        (POST) Post job for "Latitude v Sol" Plot                              
    /perseverance/position/map                                             (POST) Post job for "Latitude v Longitude" Plot                        
                                                                                                                                                  
    General Rover State Routes:                                                                                                                   
    /perseverance                                                          (GET) List all Waypoint Data                                           
    /perseverance/sol                                                      (GET) List Most Current Sol in Data                                    
    /perseverance/orientation                                              (GET) List All Orientation Data w Sol-Idx                              
    /perseverance/position                                                 (GET) List All Positioning Data w Sol-Idx        

temp

curl localhost:5015/perseverance/orientation/yaw -X POST  -H 'Content-Type: application/json' -d '{"start":"0","end":"400"}'