import numpy as np
from plotoptix import TkOptiX
from pyproj import Proj, transform
import math
from ctypes import windll
windll.shcore.SetProcessDpiAwareness(1)

"""
Ray tracing program for displaying the topography the terrain.
"""

# from coord_converter import coord_converter

inProj = Proj(init='epsg:2154')     # Lambert Conformal Conic
outProj = Proj(init='epsg:4326')    # WGS84

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

# print(coord_converter(932921.98, 6844583.18, 328))

factor = 4.0

# Create the scene
nancy_NE_raw = np.loadtxt('../selection_nancy/nancy_NE.asc', encoding='ASCII', skiprows=6)
nancy_SE_raw = np.loadtxt('../selection_nancy/nancy_SE.asc', encoding='ASCII', skiprows=6)
print("data loaded")

nancy_E_raw = np.concatenate((nancy_NE_raw, nancy_SE_raw), axis=0)
nancy_raw = nancy_E_raw

h, l = np.shape(nancy_E_raw)
#NE: xllcorner    924987.500000000000 ; yllcorner    6850012.500000000000 ; cellsize     25.000000000000
nancy_refined = np.zeros((h*l, 3), dtype=np.float64)
nancy_adapted_normalized = np.zeros((h, l, 3), dtype=np.float64)
nancy_adapted = np.zeros((h, l, 3), dtype=np.float64)
nancy_spherical = np.zeros((h, l, 3), dtype=np.float64)

alti_min = min([min(row) for row in nancy_raw])
alti_max = max([max(row) for row in nancy_raw])
print(alti_min, alti_max)

x0, y0 = 924987, 6825012    # ORIGIN

xmax, ymax = x0 + l*25, y0 + h*25
print(h, l)
# for i in range(h):
#     for j in range(l):
#         if j % 1000 == 0:
#             print((i*l + j)/(h*l)*100, "%")
        # x = j*25*factor/(xmax-x0) - factor/2
        # y = i*25*factor/(ymax-y0)*2 - factor
        # alti = (nancy_raw[h-1-i, j] - alti_min)*factor/(alti_max - alti_min) - factor/2
        # nancy_refined[i*l+j] = [x, alti, y]    # y-axis is reversed
        # nancy_adapted_normalized[i, j] = [x, alti, y]
        # nancy_adapted[i, j] = [x0+j*25, y0+i*25, nancy_raw[h-1-i, j]]   #X, Y, alti
        # nancy_spherical[i, j] = np.array(coord_converter(x0+j*25, y0+i*25, nancy_raw[h-1-i, j]))

# with open('lambert_coord_adapted.npy', 'wb') as f:
#     np.save(f, nancy_adapted)

with open('lambert_coord_adapted.npy', 'rb') as f:
    nancy_spherical = np.load(f)

# print(np.maximum(nancy_spherical, 0, nancy_spherical))
print(nancy_spherical[:50,:,:])

def small_plot(data):
    plot = TkOptiX()
    r = 0.02 * np.random.random(h*l) + 0.002
    plot.set_data("Nancy", data, r=r)
    plot.show()

def big_plot(data):
    rt = TkOptiX()

    # accumulate up to 50 frames to remove the noise:
    rt.set_param(max_accumulation_frames=10)

    # add tonal correction:
    exposure = 0.9; gamma = 2.2
    rt.set_float("tonemap_exposure", exposure)
    rt.set_float("tonemap_gamma", gamma)
    rt.add_postproc("Gamma")

    # setup camera with a good point of view:

    print(np.shape(data))
    # rt.setup_camera("cam1", cam_type="DoF",
    #                 eye=[-13, -22, 3],
    #                 target=[0, 0, 0],
    #                 up=[0, 0.9, 0.5],
    #                 aperture_radius=0.06,
    #                 aperture_fract=0.2,
    #                 focal_scale=0.62,
    #                 fov=55)
    rt.setup_camera("cam1", cam_type="DoF",
                    eye=[932923.12,6844583.52, 328],       #X, Y, alti
                    target=[933620.37, 6848061.32, 328],    #X, Y, alti
                    up=[0, 0, 1],
                    aperture_radius=0.06,
                    aperture_fract=0.2,
                    focal_scale=0.024,
                    fov=84)
    # rt.setup_camera("cam1", cam_type="DoF",                                     # setup for camera in spherical coordinates
    #                 eye=coord_converter(932923.12,6844583.52, 328),            # [932921.98, 328, 6844583.18]
    #                 target=coord_converter(933620.37, 6848061.32, 328),         #[933620.37, 328, 6848061.32]
    #                 up=coord_converter(932923.12,6844583.52, 328),
    #                 aperture_radius=0.06,
    #                 aperture_fract=0.2,
    #                 focal_scale=0.024,
    #                 fov=84)

    # add the Sun to light up the scene:
    # rt.setup_light("sun", pos=[-50, 0, 0], color=60, radius=6)

    rt.set_surface(
        "topography", data,
        wrap_v=True,
        make_normals=True)

    # rt.select()
    rt.start()

# big_plot(nancy_adapted)
big_plot(nancy_spherical)
# small_plot(nancy_adapted_normalized)