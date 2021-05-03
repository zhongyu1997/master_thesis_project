import arcgisscripting, sys, re, codecs as gps
import arcpy,os
import numpy as np
import pandas as pd
import DataPath

gp = arcgisscripting.create()

def lambda_add_date(x):
    ind = int(x[0][-4:])
    # print x
    time = x[7].replace(':','',2)[1:]
    if time[-2:] == '60':
        time = time[:-2]+'00'
    if 16 <= ind <= 181:
        return '20210325'+ time
    if 182 <= ind <= 400:
        return '20210401' + time
    if 401 <= ind <= 541:
        return '20210405' + time
    return time

def read_position(path):
    if os.path.exists(path):
        with open(path) as f:
            content = f.read().split('\n')[2:]
            for i in range(0,len(content)):
                content[i] = content[i].replace(',,,','')
                content[i] = content[i].split(',  ')
            content = np.array(content[:-1])
            gp.AddMessage('Position get.')
            return content
    else:
        gp.AddMessage('Error: %s does not exist' % path)
        sys.exit(1)


def read_time(path, content):
    if os.path.exists(path):
        with open(path) as f:
            tmp_content = f.read().split('\n')[2:-1]
            for i in range(0, len(tmp_content)):
                tmp_content[i] = tmp_content[i].split(',')
            tmp_content = np.array(tmp_content)
            time_col = np.array(map(lambda_add_date, tmp_content)).reshape(-1,1)
            # print time_col
            content = np.concatenate((content, time_col), axis = 1)
            gp.AddMessage('Date and time added.')
            return content
    else:
        gp.AddMessage('Error: %s does not exist' % path)
        sys.exit(1)

def read_signal_num(path_list, content):
    signal_num_table = pd.DataFrame(columns = ['time', 'num', 'signals'])
    for path in path_list:
        if os.path.exists(path):
            with open(path) as f:
                while True:
                    line = f.readline()
                    if line == '':
                        break
                    if '> 2021' in line: # for example: > 2021 03 25 15 57  5.0000000  0  5
                        words = re.split('[ ]+', line)[1:]
                        second = words[5].split('.')[0].zfill(2)
                        if len(second) == 1:
                            second = '0' + second
                        time = words[0]+words[1]+words[2]+words[3]+words[4]+second
                        signals =[]
                        num = int(words[-1])
                        for i in range(num):
                            signals.append(f.readline()[0:3])
                        signal_num_table = signal_num_table.append({'time':time, 'num': num, 'signals': signals}, ignore_index=True)
        else:
            gp.AddMessage('Error: %s does not exist' % path)
            sys.exit(1)
    signal_num_table = signal_num_table.set_index('time')
    gp.AddMessage('Signal table constructed.')

    # match signal information to GPS points
    empty_col = np.array([''] * len(content)).reshape(-1, 1)
    content = np.concatenate((content, empty_col), axis=1)[15:]
    signal_list = []
    # print content
    for i in range(len(content)):
        try:
            tmp = signal_num_table.loc[content[i][4]].values
        except:
            tmp = ['',[]]
            gp.AddMessage('Key value : %s not found!' % content[i][4])
        content[i][5] = tmp[0]
        signal_list.append(tmp[1])
    return content,signal_list
    # print signal_table.ix[455], signal_table.ix[456], signal_table.ix[457]
    # return signal_num_table



def to_shp(path, content, signal_table):
    spatialRef = "4326"
    gp.workspace = os.path.dirname(path)+'\\'
    basename = os.path.basename(path)
    basename2 = basename.split('.')[0] +'2'+'.shp'
    path2 = gp.workspace + '\\' + basename2

    print gp.workspace, basename2
    # create shp file
    if os.path.exists(path2):
        arcpy.Delete_management(path2)
    shp = arcpy.CreateFeatureclass_management(gp.workspace, basename2, 'POINT', '', '', '', spatialRef)

    # add fields
    arcpy.AddField_management(path2, 'Name', 'TEXT', '#', '#', 100)
    arcpy.AddField_management(path2, 'Ellp_Hgt', 'FLOAT')
    arcpy.AddField_management(path2, 'Signal_Num', 'SHORT')
    arcpy.AddField_management(path2, 'Time', 'TEXT')
    arcpy.AddField_management(path2, 'Avail_Stl', 'TEXT', '#', '#', 255)

    # instantiate insertion cursor
    cursor = arcpy.InsertCursor(shp, ["SHAPE@XY"])



    # feature = gp.CreateObject("array")  # feature array
    # part = gp.CreateObject("array")  # part array

    # add points into shp file
    for i in range(len(content)):
        new_row = cursor.newRow()  # create new row in memory
        oPoint = gp.CreateObject("point")  # instantiate point object

        pt = content[i]
        # print pt
        oPoint.y, oPoint.x = float(pt[1]), float(pt[2])
        new_row.shape = oPoint
        new_row.Name = pt[0]
        new_row.Ellp_Hgt = float(pt[3])
        if pt[5] == '':
            new_row.Signal_Num = 0
        else:
            new_row.Signal_Num = int(pt[5])
        new_row.Time = pt[4]
        new_row.Avail_Stl = ','.join(signal_table[i])
        cursor.insertRow(new_row)

    del cursor
    gp.AddMessage("Shapefile created")

    # projection. Make sure trajectory files are in the same spatial reference as the road network.
    spatial_ref = arcpy.Describe(r"C:\Users\user\Documents\classes\master\master_project\week9\test.shp").spatialReference
    if os.path.exists(path):
        arcpy.Delete_management(path)
    arcpy.Project_management(path2, path, spatial_ref)
    arcpy.Delete_management(path2)
    gp.AddMessage("Projection done.")


def gps_to_shp(position_path, time_path = '', rawdata_list = '', output = ''):
    content = read_position(position_path)
    content = read_time(time_path, content)
    content, signal_table = read_signal_num(rawdata_list[0:3], content)
    to_shp(output, content, signal_table)



position_path = DataPath.GPS_position_data_path
time_path = DataPath.GPS_time_data_path

rawdata_list = DataPath.GPS_raw_data_path
output = r'C:\Users\user\Documents\master_project_code\result\test2.shp'
gps_to_shp(position_path,time_path, rawdata_list, output)

