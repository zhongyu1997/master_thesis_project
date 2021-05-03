import DataPath
import arcpy

fields = ['SHAPE@', 'Name', 'Signal_Num', 'Time', 'Avail_Stl']

arcpy.Delete_management('tmp_segments')
arcpy.MakeFeatureLayer_management(DataPath.road_network, 'tmp_segments')
with arcpy.da.SearchCursor(DataPath.GPS_processed_data_path, fields) as cursor:
    for row in cursor:
        # print row[1:]
        # if row[2] >= 7:
        #     continue
        nearby = arcpy.SelectLayerByLocation_management('tmp_segments', 'WITHIN_A_DISTANCE', row[0], '0.005 Kilometers')
        print len(nearby)