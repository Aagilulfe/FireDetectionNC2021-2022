# Imports
from distutils.log import error
import logging
# import threading
from concurrent.futures import ThreadPoolExecutor
import numpy as np
from pyproj import Proj, transform
import math

"""
Thread pools
"""

# Main function
def main():

    # Util parameters
    inProj = Proj(init='epsg:2154')     # Lambert Conformal Conic
    outProj = Proj(init='epsg:4326')    # WGS84

    # Util function
    def coord_converter(x, y, alti):
        R = 6378137.0 + alti  # relative to centre of the earth
        longitude_deg, latitude_deg = transform(inProj, outProj, x, y)
        # print(longitude_deg, latitude_deg)
        longitude, latitude = math.radians(longitude_deg), math.radians(latitude_deg)
        # print(longitude, latitude)
        X = R * math.cos(longitude) * math.cos(latitude)
        Y = R * math.sin(longitude) * math.cos(latitude)
        Z = R * math.sin(latitude)
        return X, Y, Z

    # Test function
    def test(args):
        id, quadrant, (x0, y0) = args
        logging.info(f'Thread {id}: started')
        # logging.info(f'Thread {id}: {x0}, {y0}')

        h, l = np.shape(quadrant)
        tab = np.zeros((h, l, 3), dtype=np.float64)
        
        logging.info(f'Thread {id}: {h}, {l}')
        for i in range(h):
            for j in range(l):
                if j == 0 and i%5 == 0:
                    logging.info(f'Thread {id}: {int((i*l)/(h*l)*100)}%')
                tab[i, j] = np.array(coord_converter(x0+j*25, y0+i*25, quadrant[h-1-i, j]))
                # logging.info(f'TATA')

        logging.info(f'Thread {id}: finished')
        return tab

    # Loading data
    nancy_NE_raw = np.loadtxt('../selection_nancy/nancy_NE.asc', encoding='ASCII', skiprows=6)
    nancy_SE_raw = np.loadtxt('../selection_nancy/nancy_SE.asc', encoding='ASCII', skiprows=6)
    print("data loaded")

    # Formatting the data
    nancy_E_raw = np.concatenate((nancy_NE_raw, nancy_SE_raw), axis=0)
    nancy_raw = nancy_E_raw
    # h, l = np.shape(nancy_E_raw)
    # nancy_spherical = np.zeros((h, l, 3), dtype=np.float64)

    # Max and min values
    alti_min = min([min(row) for row in nancy_raw])
    alti_max = max([max(row) for row in nancy_raw])
    print("alti min= ", alti_min, "; alti max=", alti_max)

    x0, y0 = 924987, 6825012    # ORIGIN
    # xmax, ymax = x0 + l*25, y0 + h*25

    one = nancy_raw[:500, :]
    two = nancy_raw[500:1000, :]
    three = nancy_raw[1000:1500, :]
    four = nancy_raw[1500:2000, :]


    logging.basicConfig(format='%(levelname)s - %(asctime)s: %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
    logging.info('Starting main')

    items = [(1, one, (x0, y0+1500*25)), (2, two, (x0, y0+1000*25)), (3, three, (x0, y0+500*25)), (4, four, (x0, y0))]

    # Create a thread pool
    with ThreadPoolExecutor(max_workers=4) as executor:
        quadrants = []
        for result in executor.map(test, items):
            quadrants.append(result)
        # Submit a job to the thread pool
        # for i in range(15):
        #     executor.submit(test, i)

    # Merge the results
    nancy_spherical = np.concatenate(quadrants, axis=0)
    # Save the data
    with open('spherical_coord_latitude_thread.npy', 'wb') as f:
        np.save(f, nancy_spherical)

    logging.info('Finished main')


if __name__ == '__main__':
    main()