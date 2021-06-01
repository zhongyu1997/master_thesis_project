# import osmapi, overpass
import ReadDEMDTM,DataPath
import numpy as np
import time,json
import arcpy

meter2lat = 0.00001141
meter2lon = 0.00000899

arcpy.Delete_management('tmp_buildings')
arcpy.MakeFeatureLayer_management(DataPath.buildings_path, 'tmp_buildings')

def query_point_offline(lon, lat, radius='0.05 kilometers'):
    # start = time.time()
    tmp_point = arcpy.PointGeometry(arcpy.Point(lon,lat), arcpy.SpatialReference(4326))
    arcpy.SelectLayerByLocation_management('tmp_buildings', 'WITHIN_A_DISTANCE', tmp_point, radius)
    building_cursor = arcpy.da.SearchCursor('tmp_buildings', ["SHAPE@"])
    # end = time.time()
    # print 'the time cost for OSM query is ', end - start
    buildings = []
    for bd in building_cursor:
        nodes_info = json.loads(bd[0].JSON)
        tmp_nodelist = []
        for node in nodes_info['rings'][0]:
            tmp_nodelist.append((node[0],node[1]))
        # reorder vertices into clockwise order.
        tmp_nodelist = reorder_vertices(tmp_nodelist)
        # get height info from DSM
        tmp_building = {}
        tmp_building['nodes_top'] = ReadDEMDTM.get_DSM_height(tmp_nodelist)
        tmp_building['nodes_bottom'] = ReadDEMDTM.get_DTM_height(tmp_nodelist)
        # print('\n')
        buildings.append(tmp_building)
    return buildings


# def query_point(lon, lat, gap): # gap: meters
#     start = time.time()
#     api = overpass.API()
#     api2 = osmapi.OsmApi()
#     # print lon - gap*meter2lon, lat - gap*meter2lat, lon + gap*meter2lon, lat + gap*meter2lat
#     MapQuery = overpass.MapQuery(lat - gap*meter2lon, lon - gap*meter2lat,
#                                  lat + gap*meter2lon, lon + gap*meter2lat) # lat-gap, lon-gap, lat+gap, lon+gap
#     # MapQuery = overpass.MapQuery(-1.607979, 54.982289, -1.606181, 54.984571)
#     response = api.get(MapQuery, responseformat='json')
#     # time.sleep(1.0)
#     end = time.time()
#     print 'the time cost for query OSM is ', end - start
#     # response = api.get('way(50.746,7.154,50.748,7.157);(._;>;)',responseformat='json')
#
#     # preprocess query result. Filter out buildings.
#     buildings = []
#     for element in response['elements']:
#         if element.has_key('type') and element['type'] == 'way' and element.has_key('tags'):
#             tags = element['tags']
#             if tags.has_key('building'):
#                 tmp_nodelsit = []
#                 tmp_building = {'id': element['id']}
#                 for id in element['nodes']:
#                     node_info = api2.NodeGet(id)
#                     lon,lat = node_info['lon'], node_info['lat']
#                     tmp_nodelsit.append((lon, lat))
#
#                 # reorder vertices into clockwise order.
#                 tmp_nodelsit = reorder_vertices(tmp_nodelsit)
#                 # print tmp_nodelsit
#                 # get height info from DSM
#                 tmp_building['nodes_top'] = ReadDEMDTM.get_DSM_height(tmp_nodelsit)
#                 tmp_building['nodes_bottom'] = ReadDEMDTM.get_DTM_height(tmp_nodelsit)
#                 # print('\n')
#                 buildings.append(tmp_building)
#     del response
#     return buildings


    # with open('./test.txt','w') as f:
    #     json.dump(response,f, indent=4, ensure_ascii=False)

# reference: https://www.cnblogs.com/Roni-i/p/9058424.html
# make them in a clockwise order
def reorder_vertices(nodelist):
    tmp = np.array(map(tuple2list, nodelist))
    min_ind = np.argmin(tmp[:,0]) % len(nodelist)
    # print minlon_index
    p1 = nodelist[min_ind]
    p0 = nodelist[(min_ind-1+(len(nodelist)-1))%(len(nodelist)-1)]
    p2 = nodelist[min_ind+1]
    m = (p1[0]-p0[0]) * (p2[1]-p1[1]) - (p1[1]-p0[1])*(p2[0]-p1[0])
    if m < 0:
        return nodelist
    else:
        return list(reversed(nodelist))


def tuple2list(tmp):
    return np.array(tmp)


# api = osmapi.OsmApi()s
# print(api.WayGet(187204004))

# print query_point_offline(-1.60708, 54.98343)