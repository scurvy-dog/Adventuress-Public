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
