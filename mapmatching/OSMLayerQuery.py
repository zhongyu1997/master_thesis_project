import osmapi, overpass
api = osmapi.OsmApi()
print(api.WayGet(419838179))

api2 = api = overpass.API()
MapQuery = overpass.MapQuery(50.746,7.154,50.748,7.157)
response = api2.get(MapQuery, responseformat="xml")
print response.encode('GBK','ignore').decode('GBk')

# print http.request('GET', 'https://expired.badssl.com')