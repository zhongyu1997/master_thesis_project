from PIL import Image
import sys
import DataPath


cols = 5000
rows = 5056
cellx = 3.1421079e-005
celly = 1.7871655e-005
top = 55.024138607
left = -1.689395002
right = -1.532289605
bottom = 54.933779517

im_DSM = Image.open(DataPath.DSM_path)
im_DTM = Image.open(DataPath.DTM_path)


def get_coordinate_by_lonlat(lon, lat):
    if not ( bottom <= lat <= top and left <= lon <= right ):
        print('Error: Position out of bound!')
        sys.exit(1)
    indx = int((lon - left)/cellx)
    indy = rows - int((lat - bottom)/celly)
    return (indx-1, indy-1)

def get_DSM_height(nodelist):
    global im_DSM
    # print(im.format, im.size, im.mode)
    new_node_list = []
    final_height = 0
    for (lon,lat) in nodelist:
        height = im_DSM.getpixel(get_coordinate_by_lonlat(lon,lat))
        if final_height < height: final_height = height
        # print (lon, lat, height)
    for (lon,lat) in nodelist:
        new_node_list.append((lon, lat, final_height+50))
    return new_node_list

def get_DTM_height(nodelist):
    global im_DTM
    # print(im.format, im.size, im.mode)
    new_node_list = []
    for (lon,lat) in nodelist:
        height = im_DTM.getpixel(get_coordinate_by_lonlat(lon,lat))
        # print (lon, lat, height)
        new_node_list.append((lon, lat, height+50))
    return new_node_list

# print im.getpixel(get_coordinate_by_lonlat(lon,lat))