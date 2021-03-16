import datetime
import os
import sys
import pandas
import re
import numpy
import matplotlib.pyplot as plt

gps_time = datetime.datetime(1980, 1, 6, 0, 0, 0)
igs_folder = r'C:\Users\user\Documents\master_project_code\satellite_position'
satellite_table_x = pandas.DataFrame(columns=['date-time','PG01','PG02','PG03','PG04','PG05','PG06','PG07','PG08','PG09','PG10',
                                            'PG11','PG12','PG13','PG14','PG15','PG16','PG17','PG18','PG20','PG21','PG22','PG23',
                                            'PG24','PG25','PG26','PG27','PG28','PG29','PG30','PG31','PG32'])
satellite_table_y = pandas.DataFrame(columns=['date-time','PG01','PG02','PG03','PG04','PG05','PG06','PG07','PG08','PG09','PG10',
                                            'PG11','PG12','PG13','PG14','PG15','PG16','PG17','PG18','PG20','PG21','PG22','PG23',
                                            'PG24','PG25','PG26','PG27','PG28','PG29','PG30','PG31','PG32'])
satellite_table_z = pandas.DataFrame(columns=['date-time','PG01','PG02','PG03','PG04','PG05','PG06','PG07','PG08','PG09','PG10',
                                            'PG11','PG12','PG13','PG14','PG15','PG16','PG17','PG18','PG20','PG21','PG22','PG23',
                                            'PG24','PG25','PG26','PG27','PG28','PG29','PG30','PG31','PG32'])

def beijing_time_to_gps_week(timestamp):
    global gps_time
    beijing_time = datetime.datetime.strptime(timestamp,"%Y-%m-%d,%H:%M:%S")
    utc_time = beijing_time - datetime.timedelta(hours=8)
    gps_week = utc_time - gps_time
    week = int(gps_week.days/7)
    day = gps_week.days % 7
    hour = int((gps_week.seconds % (24 * 60 * 60))/3600)
    min = int((gps_week.seconds % 3600) / 60)
    sec = int(gps_week.seconds % 60)
    return {'week': week, 'day': day, 'hour': hour, 'min': min, 'sec': sec}

def read_igs_files(gps_start_time, gps_end_time):
    global igs_folder, satellite_table_x, satellite_table_y, satellite_table_z
    start = int(str(gps_start_time['week'])+str(gps_start_time['day']))
    end = int(str(gps_end_time['week'])+str(gps_end_time['day']))
    for igs_time in range(start, end+1):
        igs_file = igs_folder + '\\igs' + str(igs_time) + '.sp3'
        if not os.path.exists(igs_file):
            print igs_file, 'is not existed'
            sys.exit(1)
        f = open(igs_file,'r')
        raw_data = f.read().split('\n*  ')[1:]
        for section in raw_data:
            lines = section.split('\n')
            time_tmp = re.split(r"\s*", lines[0])
            date_time = str(igs_time) + '-' + str(int(time_tmp[3])*3600 + int(time_tmp[4])*60)
            record_x = {'date-time': date_time}
            record_y = {'date-time': date_time}
            record_z = {'date-time': date_time}
            for line in lines[1:]:
                if line[0:2] == 'PG':
                    single_data = re.split(r" *",line)
                    # print line
                    record_x[single_data[0]] = single_data[1]
                    record_y[single_data[0]] = single_data[2]
                    record_z[single_data[0]] = single_data[3]
            satellite_table_x = satellite_table_x.append(record_x, ignore_index=True)
            satellite_table_y = satellite_table_y.append(record_y, ignore_index=True)
            satellite_table_z = satellite_table_z.append(record_z, ignore_index=True)
    print satellite_table_x.head()
    satellite_table_x = satellite_table_x.set_index('date-time')
    satellite_table_y = satellite_table_y.set_index('date-time')
    satellite_table_z = satellite_table_z.set_index('date-time')
    return

def lagrangian_intepolation(gps_time, order):
    seconds = gps_time['hour']*3600 + gps_time['min']*60 +gps_time['sec']
    time_id =int(seconds/900) # take (id+1), id and (id-1)
    if time_id <= order/2:
        time_id = int(order/2)
    if time_id >= 95 - int((order-1)/2):
        time_id = 95 - int((order-1)/2)
    time_set = []
    for num in range(time_id-int(order/2), time_id+ int((order-1)/2)+1):
        time_set.append(str(gps_time['week']) + str(gps_time['day']) + '-' + str(num*900))
    time_set.remove(str(gps_time['week']) + str(gps_time['day']) + '-' + str(time_id*900))
    # time1 = (time_id - 1) * 900
    # time2 = time_id * 900
    # time3 = (time_id + 1) * 900
    # stamp1 = str(gps_time['week']) + str(gps_time['day']) + '-' + str(time1)
    # stamp2 = str(gps_time['week']) + str(gps_time['day']) + '-' + str(time2)
    # stamp3 = str(gps_time['week']) + str(gps_time['day']) + '-' + str(time3)
    position = []
    for table in [satellite_table_x, satellite_table_y, satellite_table_z]:
        # print table.head()
        result = numpy.array([0] * 32).reshape(-1,1).astype(float)
        for stamp in time_set:
            tmp_x = table.loc[stamp].values.reshape(-1,1).astype(float)
            tmp_result = tmp_x
            time = int(stamp.split('-')[1])
            for stamp2 in set(time_set) - set([stamp]):
                time2 = int(stamp2.split('-')[1])
                tmp_result = tmp_result * (seconds-time2)/(time-time2)
            result = result + tmp_result
        # x1 = table.loc[stamp1].values.reshape(-1,1).astype(float) # time_id - 1
        # x2 = table.loc[stamp2].values.reshape(-1,1).astype(float) # time_id
        # x3 = table.loc[stamp3].values.reshape(-1,1).astype(float) # time_id + 1
        # result = x1 * (seconds - time2)*(seconds - time3)/((time1 - time2)*(time1 - time3))+\
        #     x2 * (seconds - time1)*(seconds - time3)/((time2 - time1)*(time2 - time3))+\
        #     x3 * (seconds - time1)*(seconds - time2)/((time3-time1)*(time3-time2))
        if len(position):
            position = numpy.concatenate((position,result),axis=1)
        else:
            position = result
    # print position
    return position



timestamp = beijing_time_to_gps_week('2008-10-20,11:45:00')
# print timestamp
read_igs_files(timestamp, timestamp)

########################### verifying the accuracy ######################
order3 = lagrangian_intepolation(timestamp,4)
order4 = lagrangian_intepolation(timestamp,5)
order5 = lagrangian_intepolation(timestamp,6)
order6 = lagrangian_intepolation(timestamp,7)
order7 = lagrangian_intepolation(timestamp,8)
order8 = lagrangian_intepolation(timestamp,9)
order9 = lagrangian_intepolation(timestamp,10)
standardx = satellite_table_x.loc['15021-13500'].values.reshape(-1,1).astype(float)
standardy = satellite_table_y.loc['15021-13500'].values.reshape(-1,1).astype(float)
sandardz = satellite_table_z.loc['15021-13500'].values.reshape(-1,1).astype(float)
# print order3[1:,0].reshape(-1,1), standardx[1:]
cut_number = lambda x: float(('%.6f'%x)[-9:])
plt.plot(map(cut_number,order8[1:,0]), map(cut_number,standardx[1:]),'ro')
plt.show()