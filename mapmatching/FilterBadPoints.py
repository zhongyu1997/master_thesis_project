import DataPath
import arcpy

fields = ['SHAPE@', 'Name', 'Signal_Num', 'Time', 'Avail_Stl']

arcpy.Delete_management('tmp_segments')
arcpy.MakeFeatureLayer_management(DataPath.road_network, 'tmp_segments')
GPS_data = []
with arcpy.da.SearchCursor(DataPath.GPS_processed_data_path, fields) as cursor:
    for row in cursor:
        GPS_data.append(row)
del cursor
# print GPS_data
for row in GPS_data:
    print row[1]
    if row[2] >= 7:
        continue
    arcpy.SelectLayerByLocation_management('tmp_segments', 'WITHIN_A_DISTANCE', row[0], '0.015 Kilometers')
    tmp_cursor = arcpy.da.SearchCursor('tmp_segments', ["osm_id","SHAPE@"])
    candidate_segs = []
    for seg in tmp_cursor:
        candidate_segs.append(seg)
    del tmp_cursor
    arcpy.Delete_management('tmp_candi')
    arcpy.MakeFeatureLayer_management(row, 'tmp_candi')
    candi_cursor = arcpy.da.SearchCursor('tmp_candi', ["SHAPE@"])
    for candi in candi_cursor:
        print candi


