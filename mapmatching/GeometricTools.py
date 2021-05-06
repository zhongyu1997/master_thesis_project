from sympy import *
import math,sys
import numpy as np
import json
from AbusolutePositioning import earthfixed_to_longlat, longlat_to_earthfixed, building_to_WGS84

def distance_between(p1,p2):
    d = (p1[0]-p2[0])*(p1[0]-p2[0]) + (p1[1]-p2[1])*(p1[1]-p2[1]) + (p1[2]-p2[2])*(p1[2]-p2[2])
    return math.sqrt(d)


# first is a list, second is an object
def diff(first, second):
    return [item for item in first if item is not second]

# compute symmetric position for the candidate
# candidate_position: (x,y,z)
# building_edge: ((x,y,z),(x,y,z))
# should be in WGS84
# but the difference between figures are too small and sympy cannot solve the equations
def symmetric_position_calc(candidate_position, building_edge):
    (lon, lat, hgt) = candidate_position
    (start, end) = building_edge
    # compute symmetric position
    # lon = 100 * lon
    # lat = 100 * lat
    # start = 100 * start
    # end = 100 * end
    x = Symbol('x')
    y = Symbol('y')
    f1 = (x-start[0])**2+(y-start[1])**2-(lon-start[0])**2-(lat-start[1])**2
    f2 = (start[1]-end[1])*(y-lat)+(start[0]-end[0])*(x-lon)
    solved_value = solve([f1,f2], [x, y])
    # print solved_value
    # print type(solved_value[0][0])
    if not solved_value[0][0].is_Float:
        f3 = (x-end[0])**2+(y-end[1])**2-(lon-end[0])**2-(lat-end[1])**2
        solved_value = solve([f3, f2], [x, y])
        # print type(solved_value[0][0])
        i= 0
        while not solved_value[0][0].is_Float:
            i = i + 1
            if i>5:
                print("Error: cannot find symmetric position for the candidate (%f, %f, %f)" % candidate_position)
                print 'the edge is ', start[0], ',', start[1], 'and ', end[0], ',', end[1]
                sys.exit(1)
            # extend the line
            D = ((i+1)*end[0]-start[0], (i+1)*end[1]-start[1])
            f4 = (x-D[0])**2+(y-D[1])**2-(lon-D[0])**2-(lat-D[1])**2
            f5 = (start[1]-D[1])*(y-lat)+(start[0]-D[0])*(x-lon)
            solved_value = solve([f4, f2], [x, y])


    if abs(solved_value[0][0] - candidate_position[0]) < 0.000001:
        return (solved_value[1][0],solved_value[1][1],hgt)
    else:
        return (solved_value[0][0],solved_value[0][1],hgt)



# compute the intersection point between the line and the surface
# satellite position in earth-fixed coordinate
# rest of positions are in WGS84
# reference: https://www.jianshu.com/p/4b630c11f9f5
# all in earth-fixed
# building_top_edge: the edge on the top of the surface
# RETURN: (0,0,0) - no intersection or intersection out of bound.
def test_intersection_line_surface(satellite_position, candidate_position, building_edge, building_top_edge):
    # P: a point on the line
    # D: direction vector of the line
    # P1: a point on the plane
    # D1: normal vector of the plane
    P = candidate_position
    D = (P[0]-satellite_position[0], P[1]-satellite_position[1],
         P[2]-satellite_position[2])
    D1 = normal_vector_calc( building_edge[0],
                             building_edge[1],
                             building_top_edge[1])
    P1 = building_edge[0]
    if D[0]*D1[0]+D[1]*D1[1]+D[2]*D1[2]==0:
        return 0,0,0

    m = ((P1[0] - P[0]) * D1[0] + (P1[1] - P[1]) * D1[1] + (P1[2] - P[2]) * D1[2]) / \
        (D1[0] * D[0] + D1[1] * D[1] + D1[2] * D[2])
    # print m
    tmp_result = (P[0] + D[0] * m, P[1] + D[1] * m, P[2] + D[2] * m)
    if inside_polygon(tmp_result, building_edge[0], building_edge[1],
                      building_top_edge[1], building_top_edge[0], D1):
        return tmp_result
    else:
        return 0,0,0



def normal_vector_calc(p1,p2,p3):
    # reference for computing normal vector: https://blog.csdn.net/sinat_41104353/article/details/84963016
    a = (p2[1]-p1[1])*(p3[2]-p1[2]) - (p3[1]-p1[1])*(p2[2]-p1[2])
    b = (p2[2]-p1[2])*(p3[0]-p1[0]) - (p3[2]-p1[2])*(p2[0]-p1[0])
    c = (p2[0]-p1[0])*(p3[1]-p1[1]) - (p3[0]-p1[0])*(p2[1]-p1[1])
    return (a,b,c)


def test_intersection_segments(p1,p2,p3,p4):
    pass


# all in earth-fixed
# reference :
# https://ocw.mit.edu/courses/electrical-engineering-and-computer-science/6-837-computer-graphics-fall-2012/lecture-notes/MIT6_837F12_Lec14.pdf
# P18-P37
# Note: maxp and minp is the topright and bottomleft vertices of the bounding volume.
def test_intersection_ray_buildings(satellite_position, candidate_position, buildings_info):
    D = (satellite_position[0]-candidate_position[0],
         satellite_position[1]-candidate_position[1],
         satellite_position[2]-candidate_position[2])
    results = [0] * len(buildings_info)
    for building, i in zip(buildings_info,range(len(results))):
        tmp = np.array(map(tuple2list, building['processed_top'] + building['processed_bottom']))
        maxp = np.max(tmp,axis=0)
        minp = np.min(tmp,axis=0)
        # print maxp,minp
        if D[0] == 0:
            if not minp[0] <= satellite_position[0] <= maxp[0]: continue
        elif D[1] == 0:
            if not minp[1] <= satellite_position[1] <= maxp[1]: continue
        else:
            tx2,tx1 = binary_big((minp[0] - candidate_position[0]) / D[0], (maxp[0] - candidate_position[0]) / D[0])
            ty2,ty1 = binary_big((minp[1] - candidate_position[1]) / D[1], (maxp[1] - candidate_position[1]) / D[1])
            tz2,tz1 = binary_big((minp[2] - candidate_position[2]) / D[2], (maxp[2] - candidate_position[2]) / D[2])

            tstart = max(tx1,ty1,tz1)
            tend = min(tx2,ty2,tz2)
            # print tx1,tx2,ty1,ty2,tz1,tz2
            # print maxp,minp
            if tstart > tend:
                continue

        # test in details
        for j in range(len(building['processed_bottom'])-1):
            bottom_edge = (building['processed_bottom'][j],building['processed_bottom'][j+1])
            top_edge = (building['processed_top'][j],building['processed_top'][j+1])
            intersection = test_intersection_line_surface(satellite_position,candidate_position,
                                           bottom_edge, top_edge)
            # print intersection,bottom_edge
            if intersection!=(0,0,0):
                results[i] = 1
                break
    return results


def tuple2list(tmp):
    return np.array(tmp)


def binary_big(a,b):
    return (a,b) if a>b else (b,a)


def inside_polygon(p0, p1, p2, p3, p4, normal):
    # p0,p1,p2,p3,p4 are in three-dimensional space
    # but the algorithm to decide if a point is inside a polygon is performed in 2d space
    # so the first thing is to project points into 2d space
    # reference: https://www.geek-share.com/detail/2728302441.html
    if normal[0]!=0:
        # project in x direction
        p = (p0[1],p0[2])
        A = (p1[1],p1[2])
        B = (p2[1],p2[2])
        C = (p3[1],p3[2])
        D = (p4[1],p4[2])
    elif normal[1]!=0: # in y direction
        p = (p0[0], p0[2])
        A = (p1[0], p1[2])
        B = (p2[0], p2[2])
        C = (p3[0], p3[2])
        D = (p4[0], p4[2])
    elif normal[2]!=0: # in z direction
        p = (p0[0], p0[1])
        A = (p1[0], p1[1])
        B = (p2[0], p2[1])
        C = (p3[0], p3[1])
        D = (p4[0], p4[1])
    else:
        print 'Invalid normal vector: (0,0,0)'
        sys.exit(1)

    a = (B[0] - A[0]) * (p[1] - A[1]) - (B[1] - A[1]) * (p[0] - A[0])
    b = (C[0] - B[0]) * (p[1] - B[1]) - (C[1] - B[1]) * (p[0] - B[0])
    c = (D[0] - C[0]) * (p[1] - C[1]) - (D[1] - C[1]) * (p[0] - C[0])
    d = (A[0] - D[0]) * (p[1] - D[1]) - (A[1] - D[1]) * (p[0] - D[0])
    # print a, b, c, d
    if (a>=0 and b>=0 and c>=0 and d>=0) or (a<=0 and b<=0 and c<=0 and d<=0):
        return true
    return false


def multipath_error_calc(satellite_position, candidate_position, buildings_info):
    is_blocked = test_intersection_ray_buildings(satellite_position,candidate_position,buildings_info)
    print 'Test if the signal is blocked:', is_blocked
    if np.max(is_blocked) == 0:
        return -1
    multipath_error = []
    for i in range(len(is_blocked)):
        if is_blocked[i] == 1:
            continue
        building = buildings_info[i]
        visiable_surface = [1] * (len(building['processed_top'])-1)

        # check visiablity for each edge and store the result in the array visiable_surface(false positive)
        for j in range(len(visiable_surface)):
            lonlat_edge = (building['nodes_top'][j], building['nodes_top'][j+1])
            if hidden_surface_removal(candidate_position,lonlat_edge):
                # this edge belongs to a hidden surface
                visiable_surface[j] = 0

        # for each visiable edge (false positive)
        # construct multipath
        # and check if the multipath is blocked (check its validation)
        for j in range(len(visiable_surface)):
            if visiable_surface[j] == 0:
                continue
            top_edge = (building['processed_top'][j], building['processed_top'][j + 1])
            bottom_edge = (building['processed_bottom'][j], building['processed_bottom'][j + 1])
            lonlat_edge = (building['nodes_top'][j], building['nodes_top'][j + 1])

            # construct a multipath if it exists
            symmetric = longlat_to_earthfixed(symmetric_position_calc(earthfixed_to_longlat(candidate_position),
                                                                      lonlat_edge))
            intersection = test_intersection_line_surface(satellite_position, symmetric, bottom_edge, top_edge)
            if intersection == (0,0,0):
                continue

            # test if this path is blocked by other surfaces.
            path_valid = 1
            for k in range(len(visiable_surface)):
                if visiable_surface[k] == 0 or k == j :
                    continue
                tmp_top_edge = (building['processed_top'][k], building['processed_top'][k + 1])
                tmp_bottom_edge = (building['processed_bottom'][k], building['processed_bottom'][k + 1])
                tmp_intersect = test_intersection_line_surface(satellite_position, symmetric,tmp_bottom_edge,tmp_top_edge)
                if not tmp_intersect == (0,0,0):
                    # the path intersects with other surface, not valid!
                    path_valid = 0
                    break
            if path_valid:
                multipath_is_block = test_intersection_ray_buildings(satellite_position, symmetric, diff(buildings_info, buildings_info[i]))
                print multipath_is_block
                if np.max(multipath_is_block) == 1:
                    path_valid = 0

            if path_valid:
                error = distance_between(satellite_position, symmetric) - distance_between(satellite_position,candidate_position)
                multipath_error.append(error)

    if multipath_error == []:
        return -1
    return np.min(multipath_error)


def check_multipath(satellite_position, candidate_position, top_edge, bottom_edge):

    pass

# Return true if the given edge belongs to a hidden surface
# satellite_position and candidate_position is in earth-fixed coordinate.
# lonlat_edge is in WGS84
def hidden_surface_removal(candidate_position, lonlat_edge):
    candidate_lonlat = earthfixed_to_longlat(candidate_position)
    # back-face culling
    # using WGS84 when performing HSR
    # ignore z axis
    a = (lonlat_edge[1][0] - lonlat_edge[0][0], lonlat_edge[1][1] - lonlat_edge[0][1])
    normal = (-a[1], a[0])
    b = (lonlat_edge[0][0] - candidate_lonlat[0], lonlat_edge[0][1]-candidate_lonlat[1])
    if normal[0]*b[0]+normal[1]*b[1] < 0:
        return False
    else:
        return True


####### an example to test multipath calculation
# buildings_info = [
#     {'processed_top':[(1.0,3.0,4.0), (1.0,1.0,4.0),(-1.0,1.0,4.0),(-1.0,3.0,4.0),(1.0,3.0,4.0)],
#      'processed_bottom': [(1.0,3.0,0.0), (1.0,1.0,0.0),(-1.0,1.0,0.0),(-1.0,3.0,0.0),(1.0,3.0,0.0)],
#      'nodes_top':[(1.0,3.0,4.0), (1.0,1.0,4.0),(-1.0,1.0,4.0),(-1.0,3.0,4.0),(1.0,3.0,4.0)],
#      'nodes_bottom': [(1.0,3.0,0.0), (1.0,1.0,0.0),(-1.0,1.0,0.0),(-1.0,3.0,0.0),(1.0,3.0,0.0)]
#      },
#     {
#         'processed_top': [(5.0,3.0,4.0), (5.0,1.0,4.0),(3.0,1.0,4.0),(3.0,3.0,4.0),(5.0,3.0,4.0)],
#         'processed_bottom':[(5.0,3.0,0.0), (5.0,1.0,0.0),(3.0,1.0,0.0),(3.0,3.0,0.0),(5.0,3.0,0.0)],
#         'nodes_top': [(5.0,3.0,4.0), (5.0,1.0,4.0),(3.0,1.0,4.0),(3.0,3.0,4.0),(5.0,3.0,4.0)],
#         'nodes_bottom':[(5.0,3.0,0.0), (5.0,1.0,0.0),(3.0,1.0,0.0),(3.0,3.0,0.0),(5.0,3.0,0.0)]
#     },
# ]
# satellite = (-3.,2.,5)
# candidate = (2.,2.,0.)
# # print buildings_info
# print multipath_error_calc(satellite,candidate,buildings_info)

# print test_intersection_ray_buildings((0.00,0.00,3.0),(3.0,3.0,0.00),buildings_info)