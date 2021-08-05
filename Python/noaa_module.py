# Module for retreiving various data sets from NOAA

import math
import json
import requests

# Define Private functions for module
def GetDistance(coord1,coord2):
    R = 6372800  # Earth radius in meters
    lat1, lon1 = coord1
    lat2, lon2 = coord2
    
    phi1, phi2 = math.radians(lat1), math.radians(lat2) 
    dphi       = math.radians(lat2 - lat1)
    dlambda    = math.radians(lon2 - lon1)
    
    a = math.sin(dphi/2)**2 + \
        math.cos(phi1)*math.cos(phi2)*math.sin(dlambda/2)**2
    
    return 2*R*math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
def LoadStations():
    try:
        # Open the NOAA file that contains the WA stations list
        filename = "noaa_stations_wa.json"
        json_dict = {}

        # Open NOAA file
        with open(filename,"r") as fobject:
                json_dict = json.load(fobject)

    except FileNotFoundError:
        return "file not found"
    else:
        return json_dict

def __Iterate_Multidimensional(my_dict):
    for k,v in my_dict.items():
        if(isinstance(v,dict)):
            print(k+":")
            __Iterate_Multidimensional(v)
            continue

# Define the object class for the module to be called externally
class NOAA:
    '''NOAA Data for the position location'''
    
    def __init__ (self, coord):
        '''initialize values'''
        '''expect coord to be dictionary'''
        self.latitude = coord["latitude"]
        self.longitude = coord["longitude"]
        self.station_id = ''


    def Get_NOAA_Station(self):
        '''Loads NOAA station list & parses for closest station'''
        error_code =  None
        station_closest = {'id':'','distance':10000}

        # Open NOAA station list and return dictionary
        result = LoadStations()
        
        # Create lat/long list
        coord_vessel = [self.latitude, self.longitude]

        # Check to see if we got a error code or a dictionary returned
        if(isinstance(result,str)):
            if result == "file not found":
                error_code = "ERROR: nooa_stations_wa.json file not found."
        if(isinstance(result, dict)):
            for i in result['stations']:
                station_cord =[i['lat'],i['lng']]
                d = GetDistance(coord_vessel, station_cord)
                if d < station_closest['distance']:
                    station_closest['id'] = i['id']
                    station_closest['distance'] = d
        
        self.station_id = station_closest['id']
        return error_code

    def Get_Tide(self,tide_dict):
        # Create the parameters need for the API call
        rest_params = ''
        error_code =  None

        for k,v in tide_dict.items():
            if k == 'base_uri':
                base_uri = v
            else:
                rest_params = rest_params+k+"="+v +'&'

        # Fetch authentication token to SignalK server
        try:
            response = requests.request("GET", base_uri, params=rest_params)
            response.raise_for_status()
            # Convert response into a dictionary
            response_dict = response.json()
        except requests.exceptions.ConnectionError as err:
            error_code = err
            return error_code, None
        except requests.exceptions.HTTPError as err:
            error_code = err
            return error_code, None
        
        return error_code, response_dict