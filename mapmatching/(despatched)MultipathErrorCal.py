import math
from sympy import *
import AbusolutePositioning, OSMLayerQuery
from GeometricTools import distance_between, symmetric_position_calc,test_intersection_ray_buildings
#
# def multipath_error_calc(satellite_list, candidate_position, buildings_info):
    # 1.find the surfaces of the building that face the candidate point
    # 2.for each satellites and building surface, test intersection
    # 3.if intersects, compute multipath error.


# all in earth-fixed
# def multipath_error_calc(satellite_position, candidate_position, building_edge, building_point):
#     # return multipath error or -1
#     symmetric = symmetric_position_calc(candidate_position, building_edge)
#     intersection = intersection_point_calc(satellite_position, symmetric, building_edge, building_point)
#     if intersection == (-1,-1,-1):
#         return -1
#     minlon = min(building_edge[0][0],building_edge[1][0])
#     maxlon = max(building_edge[0][0],building_edge[1][0])
#     minlat = min(building_edge[0][1],building_edge[1][1])
#     maxlat = max(building_edge[0][1], building_edge[1][1])
#     if minlon <= intersection[0] <= maxlon and  minlat < intersection[1] < maxlat:
#         return distance_between(satellite_position,intersection) - \
#                distance_between(satellite_position, candidate_position)
#     else:
#         return -1




# despatched!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
# select edges that are face to the cadidate position
# candidate_position: (lon, lat, _)
# building = {'nodes':[...], 'id':..}
# return edge_list
# edge_list: [ ((lon,lat,hgt),(lon,lat,hgt)) ]
def select_edges(candidate_position , building):
    node_list = building['nodes']
    flag_list = [0] * len(node_list) # to indicate if they are selected
    edge_list = []
    for i in range(1,len(node_list)):
        # start from index 1 to index len()-2
        (centerx, centery, _ )= node_list[i]
        (previousx, previousy, _ ) = node_list[i-1]
        (latterx, lattery, _) = node_list[(i+1)%(len(node_list)-1)]
        v1x =  previousx - centerx
        v1y = previousy - centery
        v2x = latterx - centerx
        v2y = lattery - centery

        # compute the angles between two edge
        # formula from: https://blog.csdn.net/csxiaoshui/article/details/73498340
        theta = - math.atan2(v2y,v2x) + math.atan2(v1y,v1x)
        if theta < 0 : theta = 2*math.pi + theta
        (candidatex, candidatey,_) = candidate_position
        theta2 = - math.atan2(v2y,v2x) + math.atan2(candidatey - centery, candidatex - centerx)
        if theta2 < 0: theta2 = 2 * math.pi + theta2
        print theta,theta2
        if theta < theta2:
            flag_list[i] = 1
    for i in range(1,len(node_list)):
        if flag_list[i-1] == 1 and flag_list[i] == 1:
            edge_list.append((node_list[i-1], node_list[i]))
    print flag_list
    return edge_list







buildings_info = OSMLayerQuery.query_point(-1.61120, 54.98300, 50)
# AbusolutePositioning.building_to_earthfixed(buildings_info[0])
print buildings_info

# buildings_info = [{'processed_top':[(0.00,0.00,0.00),(1.00,0.00,0.00),(1.00,1.00,0.00),(0.00,1.00,1.00)], 'processed_bottom':[]}]

# test_intersection_ray_buildings((0.00,0.00,1.5),(1.5,0.0,0.00),buildings_info)
# edge_list = select_edges((-1.61120, 54.98300,50),buildings_info[0])
# print edge_list
# candidate = (AbusolutePositioning.longlat_to_earthfixed(edge_list[0][0]), AbusolutePositioning.longlat_to_earthfixed(edge_list[0][1]))
print symmetric_position_calc((-1.61120, 54.98300, 50),(buildings_info[0]['nodes_bottom'][0],buildings_info[0]['nodes_bottom'][1]))
# print symmetric_position_calc((-1.0,1.0, 50),[(1.0,3.0,50),(0,3.0,50)])
# print multipath_error_calc((8.0,0,8.0),(0,0,0),((4.0,4.0,0),(4.0,6.0,0)),30.0)