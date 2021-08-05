import math
from datetime import datetime, timedelta
from tzlocal import get_localzone
import pytz
from re import match, search
from signalk_module import signalk
from pytz import timezone
from noaa_module import *
from influx_module import *
from auth_credentials import signalk_ip, signalk_port, signalk_user, signalk_pass


### SETTING ENVIRONMENT VARIABLES 
# Set InfluxDb variables
influx_host = '192.168.1.115'
influx_port = '8086'
influx_db = 'SignalK'
influx_rp = 'ONE-WEEK'


# Create dictionary for NOAA Tide call
tide_api = {
    'base_uri': 'https://api.tidesandcurrents.noaa.gov/api/prod/datagetter?',
    'product': 'predictions',
    'application': 'signalk.org/node-server',
    'begin_date': (datetime.now().strftime('%Y%m%d')),
    'end_date': (datetime.now().strftime('%Y%m%d')),
    'datum': 'mllw',
    'time_zone': 'gmt',
    'units': 'metric',
    'time_zone': 'lst_ldt',
    'interval': 'hilo',
    'format': 'json',
    'station': ''
}
# Create list for writing to InfluxDb
sun_list = []
tide_list = []

# Create record incrementing counter for Influx timestamp
influx_record_offset = 0
local_tz = timezone("America/Los_Angeles")

# 
######## END ENVIRONMENT VARIABLES

######## START SECTION SIGNALK DATA
#

# Create SignalK class object
signalk_handle = signalk(signalk_user, signalk_pass, signalk_ip, signalk_port)

# Open SignalK Connection
return_code = signalk_handle.Open()

if return_code != None:
    print(datetime.now())
    exit(return_code)

# Perform API GET call to SignalK to get sunrise time
uri ="/environment/sunlight/times/sunrise"

return_code, result = signalk_handle.Get(uri)

if return_code != None:
    print(datetime.now())
    exit(return_code)

# Convert the sunset times from utc to local
dt_utc = datetime.strptime(result['value'],'%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc)
dt_local = dt_utc.astimezone(get_localzone())
# Parse value for sunset value
sunrise = str(dt_local.time())[0:5]

# Perform API GET call to SignalK to get sunset time
uri ="/environment/sunlight/times/sunset"

return_code, result = signalk_handle.Get(uri)

if return_code != None:
    print(datetime.now())
    exit(return_code)

# Convert the sunset times from utc to local
dt_utc = datetime.strptime(result['value'],'%Y-%m-%dT%H:%M:%S.%fZ').replace(tzinfo=pytz.utc)
dt_local = dt_utc.astimezone(get_localzone())
# Parse value for sunset value
#sunset = search('\d{2}:\d{2}',dt_local)
sunset = str(dt_local.time())[0:5]

# Construct timestamp construct for Influx write point 
# Write timestamp will be written in UTC that coorelates to 00:00 time of current day
local_dt = local_tz.localize(datetime.now())
local_dt = local_dt.replace(hour=0, minute=0, second=0,  microsecond=0)
utc_dt = local_dt.astimezone(pytz.UTC)
time_stamp = utc_dt


# Write out sunset/sunrise data points to InfluxDb
sun_list.append(
    {
        "fields":{
            "sunrise":sunrise,
            "sunset":sunset
        },
        "time":time_stamp,
        "measurement":"sunlight.times"
    }
)
# Create InfluxDb Object
influx_db = 'SignalK'
signalk_influx = Influx(influx_host, influx_port, influx_db)

# Open InfluxDb connection
return_code = signalk_influx.Open()

if return_code != None:
    print(datetime.now())
    exit(return_code)

# Write out the list of dictionary points to Influx
return_code = signalk_influx.Write (sun_list)

if return_code != None:
    print(datetime.now())
    exit(return_code)

# Close database handle  
signalk_influx.Close

#
########## CLOSE SECTION SIGNALK DATA


#### OPEN INFLUX AND GET LATEST GPS COORDINATES
# Create InfluxDb Object
signalk_influx = Influx(influx_host, influx_port, influx_db)

# Open InfluxDb connection
return_code = signalk_influx.Open()

if return_code != None:
    print(datetime.now())
    exit(return_code)

# Query Influxdb for gps coordinates
# Set query string
query = "select last(jsonValue) from \"navigation.position\" where time > now() -1m"

# Query Influxdb
return_code, result = signalk_influx.Query (query)

if return_code != None:
    print(datetime.now())
    exit(return_code)

# Parse the query return for latitude and longitude
for item in result:
    n1,t1 = item['last'].split(",")
    n2 = search('-*\d+\.\d+',n1)
    t2 = search('-*\d+\.\d+',t1)
    coord_vessel = {
        'longitude': float(n2.group()),
        'latitude': float(t2.group())
    }
# Close database handle    
signalk_influx.Close

#
### END GET GPS COORDINATES

# Create NOAA Class Object
vessel = NOAA(coord_vessel)

##### SECTION OF CODE TO COLLECT AND PUBLISH TIDE DATA
#

# Creat NOAA class object
return_code = vessel.Get_NOAA_Station()

if return_code != None:
    print(datetime.now())
    exit(return_code)

# Assign tide station to tide_api dictinary
tide_api['station'] = vessel.station_id

# Call NOAA to get tide data and assign to dictionary
return_code, noaa_tide_data = vessel.Get_Tide(tide_api)

if return_code != None:
    print(datetime.now())
    exit(return_code)

# Build write point for InfluxDb call.
# Influx client write operations needs a list of dictionaries.
# Loop through tide data list and create list of dictionaries
for l in noaa_tide_data['predictions']:
    date_parse = match('\d{4}-\d{2}-\d{2}',l['t'])
    time_parse = search('\d+:\d+',l['t'])

    # Construct timestamp in UTC tz based on current date
    # Construct timestamp construct for Influx write point 
    influx_record_offset += 1 
    local_dt = local_tz.localize(datetime.now())
    local_dt = local_dt.replace(hour=0, minute=influx_record_offset, second=0,  microsecond=0)
    utc_dt = local_dt.astimezone(pytz.UTC)
    time_stamp = utc_dt

    tide_list.append(
        {
            "fields":{
                "tide_time":time_parse.group(),
                "height":float(l['v']),
                "type":l['type']
            },
            "tags": {
                    "date":date_parse.group()
            },
            "time":time_stamp,
            "measurement":"tide"
        }
    )
    
     

# Create InfluxDb Object
influx_db = 'NOAA'
tide_influx = Influx(influx_host, influx_port, influx_db)

# Open InfluxDb connection
return_code = tide_influx.Open()

if return_code != None:
    print(datetime.now())
    exit(return_code)

# Write out the list of dictionary points to Influx
return_code = tide_influx.Write (tide_list)


if return_code != None:
    print(datetime.now())
    exit(return_code)

# Close database handle  
tide_influx.Close

#
#
### END SECTION NOAA TIDE PUBLISH

