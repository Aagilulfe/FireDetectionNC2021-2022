# -*- coding: utf-8 -*-
import math as ma

###############         DONNEES       #############################

#toutes les données en centimètres (m)
altitude=1066.87
d1=7729.12
d2=2362.96
a1=ma.atan(altitude/d1)
a2=ma.atan(altitude/d2)

#longueurs de référence pour le calcul de ce que vaut 5 m en horizontal
L2_pix=216/10 #pixels
L2_reel=179.06 #centimètres
L1_pix=80/10 #pixels
L1_reel=174.67 #centimètres

#pour 5m (500 cm), on fait les transformations (pour l'équivalent en pixels):
L2_5_pix=L2_pix*500/L2_reel
L1_5_pix=L1_pix*500/L1_reel

#plage de pixels sur laquelle on fait le modèle
h_p=600

#rajout de 1 dans ce cas pour corriger
fact=abs(int((d1-d2)/500)) #pour savoir combien de points en vertical on va faire (avant de prolonger la grille)
#rajouter un point proportionnel après


###############         ELABORATION DE LA GRILLE       ##############


#fonctions théoriques nécessaires
def angle_x(x):
    return float(a2+x*(a1-a2)/(d1-d2))
def l_a_x(a):
    return ma.sin(a)*500


# Création de la grille avec stockage des points dans des arrays numpy
import numpy as np
#tous les points tous les 5 m compris sur la ligne travaillée
Y_0=np.linspace(1., 1., fact+1) 

for i in range(0,fact+1):
    Y_0[i]=500*i #depuis x=0 jusqu'à x_max = d1-d2
    
#on calcule les distances donc les écarts successifs
Y=np.linspace(1., 1., fact+1) 
somme=0
for i in range(0,fact+1):
    Y[i]=l_a_x(angle_x(Y_0[i]))
    somme=somme+Y[i]

ratio=5
#on scale les données
s=h_p/somme
for i in range (0,fact+1):
    Y[i]=Y[i]*s/ratio


X1=np.linspace(1., 1., fact+1)
X2=np.linspace(1., 1., fact+1)
X3=np.linspace(1., 1., fact+1)
X4=np.linspace(1., 1., fact+1)
#X5=np.linspace(1., 1., fact+1)
#X6=np.linspace(1., 1., fact+1)
#X7=np.linspace(1., 1., fact+1)

for i in range(1,fact+1):
    Y[i]=Y[i]+Y[i-1]
print(Y)

X0=np.linspace(0., 0., fact+1)
for i in range(0,fact+1):
    X1[i]=-L2_pix+i*(L2_pix-L1_pix)/fact #on construit les points d'ordonnée selon la règle de proportionnalité 
    X2[i]=2*X1[i]
    X3[i]=3*X1[i]
    X4[i]=4*X1[i]
 

from PIL import Image, ImageTk 
import  tkinter as tk 
root = tk.Tk() 

image = Image.open("img_test_p22.png") 
photo = ImageTk.PhotoImage(image) 
 
canvas = tk.Canvas(root, width = image.size[0], height = image.size[1]) 
canvas.create_image(0,0, anchor = tk.NW, image=photo)


#changement de y
donnee_debut=800-265 #normalement pour autres images on aura pas besoin
Y_image=np.linspace(0.,0., fact+1)
Y_image[0]=donnee_debut
for i in range(1,fact+1):
    Y_image[i]=donnee_debut-Y[i-1] #on rajoute l'écart à chaque fois


#décalage des x avec le point de ligne de fuite
coord_fuite_x=600-200
for i in range(0,fact+1):
    X0[i]+=coord_fuite_x
    X1[i]=X1[i]+coord_fuite_x
    X2[i]=X2[i]+coord_fuite_x
    X3[i]=X3[i]+coord_fuite_x
    X4[i]=X4[i]+coord_fuite_x


############        VISUALTION SUR GRAPHIQUE       ###################


## grille sur le canvas
for i in range(0,fact):
    #lignes verticales
    canvas.create_line(X0[i],Y_image[i],X0[i],Y_image[i+1],fill='red')
    canvas.create_line(X1[i],Y_image[i],X1[i+1],Y_image[i+1],fill='red')
    canvas.create_line(X2[i],Y_image[i],X2[i+1],Y_image[i+1],fill='red')
    canvas.create_line(X3[i],Y_image[i],X3[i+1],Y_image[i+1],fill='red')
    canvas.create_line(X4[i],Y_image[i],X4[i+1],Y_image[i+1],fill='red')
       
    #lignes horizontales
    canvas.create_line(X0[i],Y_image[i],X1[i],Y_image[i],fill='blue')
    canvas.create_line(X1[i],Y_image[i],X2[i],Y_image[i],fill='blue')
    canvas.create_line(X2[i],Y_image[i],X3[i],Y_image[i],fill='blue')
    canvas.create_line(X3[i],Y_image[i],X4[i],Y_image[i],fill='blue')
    

canvas.create_line(X2[fact],Y_image[fact],X3[fact],Y_image[fact],fill='blue')
canvas.create_line(X1[fact],Y_image[fact],X2[fact],Y_image[fact],fill='blue')
canvas.create_line(X0[fact],Y_image[fact],X1[fact],Y_image[fact],fill='blue')
canvas.create_line(X3[fact],Y_image[fact],X4[fact],Y_image[fact],fill='blue')

canvas.pack(side=tk.RIGHT)

#création de la détection d'un point,relief

altitude=800


################     FONCTIONS DE L'INTERFACE GRAPHIQUE      ##################

def calcul_pos(alt,y):
    d=alt/ma.tan(angle_x(y))
    ind=0
    for i in range(0,fact):
        if y>Y_image[i] and y<=Y_image[i+1]:
            ind=i
    dist=d1+ind*500-d
    print("Intervalle de distance en vertical")
    return (dist/100,dist/100+5)

def clic(event):
    """ Gestion de l'événement clic gauche sur la zone graphique """
    Y = event.y
    print(calcul_pos(altitude,Y))
    label.configure(text=str(calcul_pos(altitude,Y)))

canvas.bind('<Button-1>', clic)
label = tk.Label(root, text="position")
label.pack(side = tk.LEFT)



root.mainloop()
