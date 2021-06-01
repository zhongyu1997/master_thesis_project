# This file is the main entry of the whole process
# run it after data preparation (after runing GPSDataProcessing.py)
import DataPath, SatellitePosition,GeometricTools,OSMLayerQuery, AbusolutePositioning
import arcpy, os, shutil, time
import ReadDEMDTM

time_start = time.time()
arcpy.env.workspace = DataPath.intermedia_output_path

##### 1. traverse all GPS point ##########
fields = ['SHAPE@', 'Name', 'Signal_Num', 'Time', 'Avail_Stl','SHAPE@XY']

# arcpy.Delete_management('tmp_segments')
# arcpy.MakeFeatureLayer_management(DataPath.road_network, 'tmp_segments')
timestamp = SatellitePosition.uk_time_to_gps_week('20210325155710')
SatellitePosition.read_igs_files(timestamp,timestamp)
arcpy.Delete_management('tmp_segments')
arcpy.MakeFeatureLayer_management(DataPath.road_network, 'tmp_segments')
i = 16
with arcpy.da.SearchCursor(DataPath.GPS_processed_data_path, fields) as cursor:
    for row in cursor:
        print row[1]
        i = i + 1
        if not i == 39:
            continue
        if row[2] >= 8:
            continue
        measure_GPS = ReadDEMDTM.get_DSM_height(row[5])
        measure_GPS = AbusolutePositioning.longlat_to_earthfixed(measure_GPS)
        ############### 2. get satellites position using the timestamp ###################
        tmp_time = SatellitePosition.uk_time_to_gps_week(str(row[3]))
        satellites_loc = SatellitePosition.lagrangian_intepolation(tmp_time, 9)
        # print satellites_loc
        avail_stl = row[4].split(',')
        # print avail_stl
        if len(avail_stl) >= 2:
            avail_stl = list(map(lambda x: int(x[1:]),avail_stl))
            ################### 3. find some possible candidate points ###################
            arcpy.SelectLayerByLocation_management('tmp_segments', 'WITHIN_A_DISTANCE', row[0], '0.03 Kilometers')
            seg_cursor = arcpy.da.SearchCursor('tmp_segments',["osm_id", "SHAPE@"])
            segs = []
            for seg in seg_cursor:
                segs.append(seg)
            del seg_cursor
            if len(segs) < 2:
                continue
            for seg in segs:
                # get the candidate position
                io_time_start = time.time()
                candidates = GeometricTools.get_points_along_polyline(row[5], seg[1])
                io_time_end = time.time()
                print 'the time cost for finding candidates: ', io_time_end-io_time_start
                for can_info in candidates:
                    # get candidate height
                    candidate = can_info
                    candidate = ReadDEMDTM.get_DTM_height(candidate)
                    candidate = AbusolutePositioning.longlat_to_earthfixed(candidate)
                    # get buildings info
                    buildings_info = OSMLayerQuery.query_point_offline(can_info[0], can_info[1])
                    if len(buildings_info) < 2:
                        continue
                    AbusolutePositioning.buildings_to_earthfixed(buildings_info)
                    pseudo_errors = []
                    pseudo_satellites = []
                    for sate_ind in avail_stl:
                        # for each satellite, compute multipath error
                        pseudo = [0.,0.,0.,0.]
                        pseudo[1],pseudo[2],pseudo[3] = satellites_loc[sate_ind-1]
                        pseudo[0] = GeometricTools.distance_between(satellites_loc[sate_ind-1], candidate)
                        multi_error = GeometricTools.multipath_error_calc(satellites_loc[sate_ind-1],candidate,buildings_info)
                        pseudo_errors.append(multi_error)
                        if multi_error != -1:
                            pseudo[0] += multi_error
                        pseudo_satellites.append(pseudo)
                    print 'the multipath errors for this candidate is ', pseudo_errors
                    if max(pseudo_errors) == -1:
                        continue
                    # print 'the pseudo range and satellite positions are ', pseudo_satellites

                    # up to now, we get the multipath error for this single candidate
                    ############ 4. using abusolute positioning to compute the position ##################
                    hypothesis_GPS = AbusolutePositioning.absolute_positioning(pseudo_satellites, candidate)
                    print 'the estimated position for this candidate is ',hypothesis_GPS
                    print 'distance between hypothesis GPS point and measured GPS point is (km):', GeometricTools.distance_between(hypothesis_GPS,measure_GPS)

    time_end = time.time()
    print 'total time cost (seconds): ', time_end-time_start


            # tmp_near_table[0].save(DataPath.intermedia_output_path+r'\tmp_data')
            # break
            # table_cursor = arcpy.da.SearchCursor(tmp_near_table, ['NEAR_FID', 'NEAR_DIST', 'NEAR_X', 'NEAR_Y'])
            # for record in table_cursor:
            #     print record
                # candidate = GeometricTools.get_drop_foot(row[5],)


        # buildings_info = OSMLayerQuery.query_point(row[5][0],row[5][1],20)
        # for stl_ind in avail_stl:
        #     multi_err = GeometricTools.multipath_error_calc(satellites_loc[stl_ind-1], row[5],buildings_info)
        #     print 'the satellite is ', stl_ind, ', and error is ', multi_err
        # nearby = arcpy.SelectLayerByLocation_management('tmp_segments', 'WITHIN_A_DISTANCE', row[0], '0.005 Kilometers')
        # print len(nearby)