
import extcolors
from PIL import Image
import numpy as np
import simulation
import sys
global path, nb_iter, Vx, Vy, speed
# path to the image
path = "foret.png"

nb_iter = 100

Vx = None
Vy = None
speed = 4

for i in range(1, len(sys.argv)):

    if sys.argv[i] == "--img":
        path = str(sys.argv[i+1])
        i = i+1
    if sys.argv[i] == "--iter":
        nb_iter = int(sys.argv[i+1])
        i = i+1
    if sys.argv[i] == "--Vx":
        Vx = float(sys.argv[i+1])
        i = i+1
    if sys.argv[i] == "--Vy":
        Vy = float(sys.argv[i+1])
        i = i+1
    if sys.argv[i] == "--speed":
        speed = int(sys.argv[i+1])
        i = i+1

print(path)
# cherche les couleurs dominantes
res, _ = extcolors.extract_from_path(path, 20, 2)
colors = []
for value, nb in res:
    colors += [value]
print(colors)


# 1000m=157pixel
scale = 1000/157


# recolorie l'image avec les coleurs dominantes
img = Image.open(path)
width, height = img.size
L = 100
height_grid, width_grid = int(height*scale/L), int(width*scale/L)
print(height, width)
print(height_grid, width_grid)
colors_ind = []
for i in range(height):
    colors_ind.append([0]*width)
print(len(colors_ind[0]))
for i in range(height):
    for j in range(width):
        pixel = img.getpixel((j, i))
        # find the closest color
        closest = min(colors, key=lambda c: abs(
            c[0]-pixel[0])*255*255+abs(c[1]-pixel[1])*255+abs(c[2]-pixel[2]))
        img.putpixel((j, i), closest)
        colors_ind[i][j] = colors.index(closest)

img.save(path+"_color.png")
nb = int(L/scale)

im = Image.new(mode="RGB", size=((width_grid)*nb, (height_grid)*nb))


grid = []
for i in range(height_grid):
    grid.append([0]*width_grid)

fuel = [300, 200]

# moyenne les couleurs en fonction de l'échelle
for i in range(height_grid):
    for j in range(width_grid):
        mean = 0
        index = 0
        for k in range(nb):
            for l in range(nb):
                mean += colors_ind[i*int(nb)+k][j*int(nb)+l]
        mean /= nb*nb
        if mean > 0.5:
            index = 1
        # création du grid pour la simulation
        grid[i][j] = simulation.zone(0, fuel[index], i, j)
        color = colors[index]
        for k in range(nb):
            for l in range(nb):
                im.putpixel((j*int(nb)+k, i*int(nb)+l), color)

im.save(path+"_mean.png")

simulation.simulation(L, height_grid, width_grid, grid, nb_iter, speed, Vx, Vy)
