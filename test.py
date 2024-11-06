import json

with open('static/us_counties.geojson') as f:
    geojson_data = json.load(f)

# Print the properties of the first feature
print(geojson_data['features'][0]['properties'])
