# This file is the main entry of the whole process
# run it after data preparation (after runing GPSDataProcessing.py)
import DataPath, SatellitePosition,GeometricTools,OSMLayerQuery, AbusolutePositioning
import arcpy, os, shutil
import ReadDEMDTM

arcpy.env.workspace = DataPath.intermedia_output_path

##### 1. traverse all GPS point ##########
fields = ['SHAPE@', 'Name', 'Signal_Num', 'Time', 'Avail_Stl','SHAPE@XY']

# arcpy.Delete_management('tmp_segments')
# arcpy.MakeFeatureLayer_management(DataPath.road_network, 'tmp_segments')
time = SatellitePosition.uk_time_to_gps_week('20210325155710')
SatellitePosition.read_igs_files(time,time)
arcpy.Delete_management('tmp_segments')
arcpy.MakeFeatureLayer_management(DataPath.road_network, 'tmp_segments')
i = 15
with arcpy.da.SearchCursor(DataPath.GPS_processed_data_path, fields) as cursor:
    for row in cursor:
        print row[1]
        i = i + 1
        if not i == 32:
            continue
        if row[2] >= 8:
            continue
        ##### 2. get satellites position using the timestamp ##########
        tmp_time = SatellitePosition.uk_time_to_gps_week(str(row[3]))
        satellites_loc = SatellitePosition.lagrangian_intepolation(tmp_time, 9)
        # print satellites_loc
        avail_stl = row[4].split(',')
        # print avail_stl
        if len(avail_stl) >= 2:
            avail_stl = list(map(lambda x: int(x[1:]),avail_stl))
            ##### 3. find some possible candidate points ##########
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
                tmp_row = DataPath.intermedia_output_path + r'\tmp_row.shp'
                tmp_seg = DataPath.intermedia_output_path + r'\tmp_seg.shp'
                if arcpy.Exists(tmp_row): arcpy.Delete_management(tmp_row)
                if arcpy.Exists(tmp_seg): arcpy.Delete_management(tmp_seg)
                arcpy.CopyFeatures_management(row[0], tmp_row)
                arcpy.CopyFeatures_management(seg[1], tmp_seg)

                arcpy.Near_analysis(tmp_row, tmp_seg,location='LOCATION')
                candidate_cursor = arcpy.da.SearchCursor(tmp_row, ["SHAPE@", "NEAR_X", "NEAR_Y", "NEAR_DIST"])
                for can_info in candidate_cursor:
                    # get candidate height
                    candidate = (can_info[1], can_info[2])
                    candidate = ReadDEMDTM.get_DTM_height(candidate)
                    candidate = AbusolutePositioning.longlat_to_earthfixed(candidate)
                    # get buildings info
                    buildings_info = OSMLayerQuery.query_point(can_info[1], can_info[2], 50)
                    if len(buildings_info) < 2:
                        continue
                    AbusolutePositioning.buildings_to_earthfixed(buildings_info)
                    pseudo_errors = []
                    for sate_ind in avail_stl:
                        # for each satellite, compute multipath error
                        multi_error = GeometricTools.multipath_error_calc(satellites_loc[sate_ind-1],candidate,buildings_info)
                        pseudo_errors.append(multi_error)
                    print 'the multipath errors for this candidate is ', pseudo_errors
                arcpy.Delete_management(tmp_row)
                arcpy.Delete_management(tmp_seg)

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