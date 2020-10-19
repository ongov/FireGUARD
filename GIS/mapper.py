"""Code to programatically update ArcGIS sandbox server"""

# https://community.esri.com/thread/186020-start-stop-map-service-arcpy
# Demonstrates how to stop or start all services in a folder

import sys
sys.path.append('..\util')
import common

# For Http calls
import httplib, urllib, json

# For system tools
import sys


## Connection credentials for ArcGIS server
CONNECTION = {
    'username': common.CONFIG.get('FireGUARD', 'mapper_username'),
    'password': common.CONFIG.get('FireGUARD', 'mapper_password'),
    'serverName': common.CONFIG.get('FireGUARD', 'mapper_server'),
    'serverPort': common.CONFIG.get('FireGUARD', 'mapper_port'),
}

def getToken():
    """A function to generate a token given username, password and the adminURL."""
    # Token URL is typically http://server[:port]/arcgis/admin/generateToken
    tokenURL = "/arcgis/admin/generateToken"
    params = urllib.urlencode({'username': CONNECTION['username'],
                                'password': CONNECTION['password'],
                                'client': 'requestip',
                                'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    # Connect to URL and post parameters
    httpConn = httplib.HTTPSConnection(CONNECTION['serverName'], CONNECTION['serverPort'])
    httpConn.request("POST", tokenURL, params, headers)
    # Read response
    response = httpConn.getresponse()
    if (response.status != 200):
        httpConn.close()
        print "Error while fetching tokens from admin URL. Please check the URL and try again."
        return
    else:
        data = response.read()
        httpConn.close()
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):
            return
        # Extract the token from it
        token = json.loads(data)
        return token['token']


def assertJsonSuccess(data):
    """A function that checks that the input JSON object is not an error object."""
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        print "Error: JSON object returns an error. " + str(obj)
        return False
    else:
        return True

## Dictionary of services by folder that they are in
SERVICES_BY_FOLDER = {}

def startOrStopServices(stopOrStart, folder, whichServices=None):
    """Start or stop services"""
    # Check to make sure stop/start parameter is a valid value
    if str.upper(stopOrStart) != "START" and str.upper(stopOrStart) != "STOP":
        print "Invalid STOP/START parameter entered"
        return
    # Get a token
    token = getToken()
    if token == "":
        print "Could not generate a token with the username and password provided."
        return
    # Construct URL to read folder
    if str.upper(folder) == "ROOT":
        folder = ""
    else:
        folder += "/"
    folderURL = "/arcgis/admin/services/" + folder
    # This request only needs the token and the response formatting parameter 
    params = urllib.urlencode({'token': token, 'f': 'json'})
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}
    # Connect to URL and post parameters    
    httpConn = httplib.HTTPSConnection(CONNECTION['serverName'], CONNECTION['serverPort'])
    if not SERVICES_BY_FOLDER.has_key(folder):
        httpConn.request("POST", folderURL, params, headers)
        # Read response
        response = httpConn.getresponse()
        if (response.status != 200):
            httpConn.close()
            print "Could not read folder information."
            return
        data = response.read()
        # Check that data returned is not an error object
        if not assertJsonSuccess(data):          
            print "Error when reading folder information. " + str(data)
            return
        services = []
        # Deserialize response into Python object
        dataObj = json.loads(data)
        httpConn.close()
        # Loop through each service in the folder and stop or start it    
        for item in dataObj['services']:
            fullSvcName = item['serviceName'] + "." + item['type']
            services.append(fullSvcName)
        SERVICES_BY_FOLDER[folder] = services
    services = SERVICES_BY_FOLDER[folder]
    if not whichServices:
        # do everything if nothing specified
        whichServices = services
    if str == type(whichServices):
        # special case a single item to make it a list
        whichServices = [whichServices]
    bad_service = False
    for service in whichServices:
        if service not in services:
            print "Invalid service requested: " + service
            bad_service = True
    if bad_service:
        return
    for fullSvcName in whichServices:
        # Construct URL to stop or start service, then make the request
        stopOrStartURL = "/arcgis/admin/services/" + folder + fullSvcName + "/" + stopOrStart
        httpConn.request("POST", stopOrStartURL, params, headers)
        # Read stop or start response
        stopStartResponse = httpConn.getresponse()
        if (stopStartResponse.status != 200):
            httpConn.close()
            print "Error while executing stop or start. Please check the URL and try again."
            return
        else:
            stopStartData = stopStartResponse.read()
            # Check that data returned is not an error object
            if not assertJsonSuccess(stopStartData):
                if str.upper(stopOrStart) == "START":
                    print "Error returned when starting service " + fullSvcName + "."
                else:
                    print "Error returned when stopping service " + fullSvcName + "."
                print str(stopStartData)
            else:
                print "Service " + fullSvcName + " processed " + stopOrStart + " successfully."
        httpConn.close()


def stopServices(folder, whichServices=None):
    """Stop servies"""
    startOrStopServices('STOP', folder, whichServices)


def restartServices(folder, whichServices=None):
    """Stop and then start services"""
    startOrStopServices('STOP', folder, whichServices)
    startOrStopServices('START', folder, whichServices)

def startServices(folder, whichServices=None):
    """Start services"""
    startOrStopServices('START', folder, whichServices)

