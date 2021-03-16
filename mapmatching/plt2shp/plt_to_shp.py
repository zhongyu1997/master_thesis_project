#################################################################
# Author: Anna Klimaszewski-Patterson
# Date: 11 April 2010
# Purpose: Convert plt file to a shapefile with feature name and description as
#          attributes
# -- Tested with file format from OziExplorer Track Point File Version 2.1
# -- Assumes format: LATITIUDE, LONGITUDE, START_OF_TRACK(0/1).
# ---- I ignore the rest of the fields
#################################################################

import arcgisscripting, sys, re, codecs, gpsFiles as gps
import arcpy,os

try:    
#################################################################
# Function definitions
#################################################################

    #################################################################
    # Function: getData
    # Parameters: inFilename
    # Purpose: Parse data into an array
    # Returns: array
    #################################################################
    def getData(inFilename):
        # read file into variable
        contents = codecs.open(inFilename, 'rb').read()
        x = 0
        aCoords = []
        contents = contents.split("\r\n")
        for line in contents:
            if( x < 6):
                x += 1
            else:
                aLine = line.split(',')
                try:
                    aCoords.append([float(aLine[0]), float(aLine[1]), int(aLine[2])])
                except:
                    #don't really do anyline, new line wasn't truncated
                    y = 1
            # gp.AddMessage("processed line: %s" % line)
        # gp.AddMessage("aCoords: %s" % aCoords)
        return aCoords

    #################################################################
    # Function: handleData
    # Parameters: featureType (what type of data to extract)
    #             xml (XML object)
    # Purpose: handle the data by directing the processing to the
    #          correct handler (point,polyline,polygon)
    # Returns: array
    #################################################################
    def handleData(featureType, aData):
        global gp
        numFeatures = 0

        # gp.AddMessage("print adata: %s" % aData[0][2])
        # if featureType == "POLYLINE" and aData[0][2] == 0:
        #     aData[0][2] = 1
        #     gp.AddMessage("print adata: %s" % aData[0][2])

        aData = handleTracks(aData, featureType)
            
        if list(aData):
            numFeatures = len(aData)

        gp.AddMessage("%s %s features aquired" % (numFeatures, featureType))

        if numFeatures < 1:
            gp.AddMessage("Not found. Aborting...")
            sys.exit(1)

        return aData
    
    ##------------------- Track processing -----------------------##
    
    #################################################################
    # Function: handleTracks
    # Parameters: aData (array of coordinate data)
    # Purpose: Find tracks and return the data
    # Returns: array
    #################################################################
    def handleTracks(aData, featureType):
        aCoord = []
        
        name = ''
        desc = ''
        aSeg = []

        # process track segments
        if featureType == 'POLYLINE':
            for line in aData:
                # gp.AddMessage("line: %s" % line)
                if line[2] == 1: #indicates line segment
                    if aCoord: # if this is not the first segment
                        aSeg.append([name, desc, '', aCoord])
                    aCoord = [] #instantiate/clear variable
                    aCoord.append([line[0],line[1]])
                else:
                    aCoord.append([line[0],line[1]])
            aSeg.append([name, desc, '', aCoord])
            # gp.AddMessage("aSeg: %s" % aSeg)
        else:
            for line in aData:
                # aCoord.append([line[0], line[1]])
                aSeg.append([name, desc, '', [line[0], line[1]]])
        gp.AddMessage("aSeg: %s" % aSeg)
        return aSeg            

#################################################################
# Guts
#################################################################
    # create geoprocessor...
    gp = arcgisscripting.create()
    gp.OverwriteOutput = 1

    # script parameters...
    inFilename  = sys.argv[1]         # input file
    outFilename = sys.argv[2]         # output file
    featureType = sys.argv[3]
    spacialType = sys.argv[4]         # spacial reference. 0:"WGS 1984". 1: other projection
    
    # test validity of output filename (no special characters)
    gps.checkFilenameValid(outFilename, gp)

    # if validated, proceed                      
    gp.AddMessage("Retrieving %s data from PLT file..." % featureType)
    aData = getData(inFilename)
    
    # process data
    aData = handleData(featureType, aData)

    ##--------------------- Create Shapefile ------------------------##
    gp.AddMessage("Generating shapefile...")
    gp.AddMessage("Input and output: %s" % sys.argv )
    gps.createShapefile(gp, aData, sys.argv)
    gp.AddMessage("Conversion complete")

    ##--------------------- Project Shapefile ------------------------##
    if spacialType == '1':
        gp.AddMessage("Projection begin...")
        try:
            # create a spatial reference object to be used as output coordinate system
            spatial_ref = arcpy.Describe("../../Beijing/Beijing_Links.shp").spatialReference

            # use the output of CreateSpatialReference as input to Project tool
            # to reproject the shapefile
            basename = os.path.basename(sys.argv[2])
            arcpy.Project_management(sys.argv[2], "C:\\Users\\user\\Documents\\master_project_code\\result\\"+basename, spatial_ref)
            gp.AddMessage("Projection succeeded!")
            gp.AddMessage("Deleting intermediate files...")
            arcpy.Delete_management(sys.argv[2])
            gp.AddMessage("Done.")

        except arcpy.ExecuteError:
            # print geoprocessing message
            print(arcpy.GetMessages(2))

        except Exception as ex:
            # print the exception message
            print(ex.args[0])


except:
    gps.handleException(sys, gp)
