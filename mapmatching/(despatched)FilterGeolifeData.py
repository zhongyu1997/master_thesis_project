import os
import sys
import shutil

# filter trajectory data:
# 1. use bus, car or taxi
# 2. within a certain region

def filter_geolife_data(data_folder, target_folder):
    if not os.path.exists(data_folder):
        print data_folder, 'is not existed'
        sys.exit(1)
    users_folder = os.listdir(data_folder)
    for user in users_folder:
        label_path = data_folder + os.sep + user + os.sep + "labels.txt"
        if not os.path.exists(label_path):
            continue
        traffic_data = filter_label_data(label_path)
        for data in traffic_data:
            data_path = data_folder + os.sep + user + os.sep + "trajectory" + os.sep + data + '.plt'
            if str(data)[0:6] == '200810': # filter data in Oct. 2008
                if os.path.exists(data_path):
                    flag = filter_Beijing_data(data_path)
                    if flag:
                        target_path = target_folder + os.sep + user + '_' + data + '.plt'
                        shutil.copyfile(data_path, target_path)
    return

def filter_label_data(label_path):
    with open(label_path) as file:
        traffic_data = []
        for line in file:
            line=line.replace('\n', '')
            line_data = line.split('\t')
            if line_data[2] == 'bus' or line_data[2] == 'taxi' or line_data[2] == 'car':
                traffic_data.append(filter(str.isdigit, line_data[0]))
    return traffic_data

def filter_Beijing_data(data_file):
    # filter out data in a certain range
    flag = True
    with open(data_file) as file:
        for line in file:
            line_data = line.split(',')
            if len(line_data) == 7:
                if 39.825 <= float(line_data[0]) <= 40.022 and 116.261 <= float(line_data[1]) <= 116.489:
                    continue
                else:
                    # print(data_file)
                    # print(line_data[0]+' , '+line_data[1])
                    flag = False
                    break
    # print(flag)
    return flag

def statistic_data(data_folder):
    data = os.listdir(data_folder)
    statistic = set()
    for name in data:
        file_name = name.split('_')[1]
        if file_name[0:6] == '200810':
            # statistic.append(file_name[6:8])
            statistic.add(file_name[6:8])
        # if statistic.has_key(file_name[0:6]):
        #     statistic[file_name[0:6]] += 1
        # else:
        #     statistic[file_name[0:6]] = 1
    print statistic
    return


data_folder = r'C:\Users\user\Documents\master_project_code\Geolife Trajectories 1.3\Data'
target_folder = r'C:\Users\user\Documents\master_project_code\Data'
filter_geolife_data(data_folder, target_folder)
# statistic_data(target_folder)