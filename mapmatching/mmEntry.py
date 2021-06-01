import mapmatcher
import DataPath
import time
# start = time.time()
# mapmatcher.mapMatch(DataPath.GPS_processed_data_path, DataPath.road_network, 50, 50, 50)
opt = mapmatcher.mapMatch(DataPath.Trajectory_data_path[6], DataPath.road_network, 30, 25, '0.03 kilometers')
mapmatcher.exportPath(opt, 'output_0407.shp')
# end = time.time()
# print 'total time cost: ', end-start
opt2 = mapmatcher.mapMatch(DataPath.Trajectory_data_path[6], DataPath.road_network, 30, 25, '0.03 kilometers', multipath=False)
mapmatcher.exportPath(opt2, 'output_0407_origin.shp')