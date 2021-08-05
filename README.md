# Adventuress-Public
### Git repository for MV-Adventuress Public Content

### Grafana
#### Victron Dashboard + Flowchart
The Victron dashboard uses the Grafana Flowchart plugin. There are two files. 
One is the Grafana export of the dashboard and the second is the XML export
that defines the actual diagram you see including location, shapes, and colors.

Flowchart requires you to setup queries with defined Aliases that are then
referenced in the mapping section. The mapping is where all the logic runs
that dictates what is displayed in the various dashboard objects. Then in the
mapping section you tie the logic + query to an object id on the dashboard.

You will need to use the Inspect section to look at and find the object ID you
wish to reference and then insert it into the correct mapping logic.

#### Anchored Dashboard 
This dashboard I use while at anchor. Two items of note are the tide table 
panel and the anchor distance panel. Tide table is covered in detail at 
https://mv-adventuress.azurewebsites.net/ blog post. The anchored distance
is data points generated from a Node Red flow.

### Python
* telemetry_pull - main program that handles various telemetry tasks
* influx_module - module that handles all influx operations
* singalk_module - module that handles API token and GET requests
* noaa_module - module that handles calls into NOAA databases
* noaa_stations_wa.json - file that lists all the NOAA tide stations in WA state. 
* auth_credentials.py - file to import various user credentials that are needed.
