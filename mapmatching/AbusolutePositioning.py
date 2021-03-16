import numpy as np
import math

a = 6378137.0
b = 6356752.31424518

### psudeorange_and_satellite_positions should be a n*4 matrix.
### The first coloumn should be the hypothesized psudeorange.
### The rest coloumns are the X, Y, Z coordinates under the earth-fix coordinate system
def absolute_positioning(psudeorange_and_satellite_positions):
    X = np.array([100,0,0])
    delta_x  = np.array([200.0,1.0,1.0])
    while not np.all(abs(delta_x) < 1):
        # construct matrix A and L
        A = []
        L = []
        for range in psudeorange_and_satellite_positions:
            rou = math.sqrt(math.pow(range[1] - X[0], 2) + math.pow(range[2] - X[1], 2) + math.pow(range[3] - X[2], 2))
            # print 'rou is:', rou
            b0 = float((X[0]-range[1]))/rou
            b1 = float((X[1]-range[2]))/rou
            b2 = float((X[2]-range[3]))/rou
            # b3 = 1
            tmp = np.array([b0,b1,b2])
            if len(A):
                A = np.concatenate((A, tmp), axis=0)
            else:
                A = tmp
            L.append(range[0]-rou)
        A = A.reshape(-1,3)
        L = np.array(L).reshape(-1,1)
        # print 'matrix A is:', A
        # print 'matrix L is:', L
        # (A^T * A)^-1
        X_bar = np.linalg.inv(np.matmul(np.transpose(A), A))
        # (A^T * A)^-1 * A^T * L
        X_bar = np.matmul(X_bar, np.matmul(np.transpose(A), L))
        delta_x = X_bar.flatten()
        X = X + delta_x
        print 'X is:', X
        print 'delta x is:', delta_x
    return X



def longlat_to_earthfixed(long, lat, height):
    global a,b
    E = (a * a - b * b) / (a * a)
    COSLAT = math.cos(lat * math.pi / 180)
    SINLAT = math.sin(lat * math.pi / 180)
    COSLONG = math.cos(long * math.pi / 180)
    SINLONG = math.sin(long * math.pi / 180)
    N = a / (math.sqrt(1 - E * SINLAT * SINLAT))
    NH = N + height
    X = NH * COSLAT * COSLONG
    Y = NH * COSLAT * SINLONG
    Z = (b * b * N / (a * a) + height) * SINLAT
    return np.array([X,Y,Z])


def earthfixed_to_longlat(x, y, z):
    global a,b
    c = math.sqrt((a * a - b * b) / (a * a))
    d = math.sqrt((a * a - b * b) / (b * b))
    p = math.sqrt((x * x) + (y * y))
    q = math.atan2((z * a), (p * b))
    long = math.atan2(y, x)
    lat = math.atan2((z + (d * d) * b * math.pow(math.sin(q), 3)),
                     (p - (c * c) * a * math.pow(math.cos(q), 3)))
    N = a / math.sqrt(1 - ((c * c) * math.pow(math.sin(lat), 2)))
    alti = (p / math.cos(lat)) - N
    long = long * 180.0 / math.pi
    lat = lat * 180.0 / math.pi
    return np.array([long,lat,alti])



import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
data = [[173.205,100.02,-99.998,99.9876],[173.2051,100.10,-100.10,-100.06],[173.21,100.10,99.91,100.0213],[200.41,200.01,0.02,200.01]]
result = absolute_positioning(data)
# three dimensional
x = [x[1] for x in data]
y = [y[2] for y in data]
z = [z[3] for z in data]

fig = plt.figure()
ax = Axes3D(fig)
ax.scatter(x, y, z, c = 'b', label = 'Satellite positions')
ax.scatter(result[0], result[1], result[2],c = 'r', label = 'result')
ax.scatter(200,0,0,c = 'g', label = 'proposed result')

ax.set_zlabel('Z', fontdict={'size': 15, 'color': 'red'})
ax.set_ylabel('Y', fontdict={'size': 15, 'color': 'red'})
ax.set_xlabel('X', fontdict={'size': 15, 'color': 'red'})
plt.show()

# print longlat_to_earthfixed(116,40,0)
# print earthfixed_to_longlat(-2144821.8415475,4397536.46122802,4077985.57220038)