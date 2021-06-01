import arcpy

try:
    # create a spatial reference object to be used as output coordinate system
    spatial_ref = arcpy.Describe("../result/20080829112151_polyline.shp").spatialReference

    # use the output of CreateSpatialReference as input to Project tool
    # to reproject the shapefile
    arcpy.Project_management("C:\\Users\\user\\Documents\\master_project_code\\result\\Beijing_Links.shp", "C:\\Users\\user\\Documents\\master_project_code\\result\\Beijing_4326.shp",
                             spatial_ref)


except arcpy.ExecuteError:
    # print geoprocessing message
    print(arcpy.GetMessages(2))

except Exception as ex:
    # print the exception message
    print(ex.args[0])