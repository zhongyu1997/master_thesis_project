import numpy as np

framedim = [2048,2048]

nb_elem = framedim[0]*framedim[1]

offset = 4096

formatdata = np.uint16

path =
f = open(path, 'rb')

f.seek(offset)#TODO: only header size for tiff !!

d = np.fromfile(f, dtype=formatdata, count=nb_elem).reshape(framedim)