# -*- coding: utf-8 -*-
import math as ma

###############         DONNEES       #############################

taille=25000
ratio=3
#toutes les données en centimètres (m)
altitude=(315-18)*10**2
d1=404989
d2=223121
a1=ma.atan(altitude/d1)
a2=ma.atan(altitude/d2)

#longueurs de référence
L2_pix=24 #pixels
L2_reel=17965 #centimètres
L1_pix=94 #pixels
L1_reel=77129 #centimètres

#pour taille m, on fait les transformations (pour l'équivalent en pixels):
L2_5_pix=L2_pix*taille/L2_reel
L1_5_pix=L1_pix*taille/L1_reel


#plage de pixels sur laquelle on fait le modèle
h_p=90  #mesure à prendre sur la photo non scale
#points à corriger
#rajout de 1 dans ce cas pour corriger
fact=abs(int((d1-d2)/taille)) #pour savoir combien de points en vertical on va faire (avant de prolonger la grille)


###############         ELABORATION DE LA GRILLE       ##############


#fonctions théoriques nécessaires
def angle_x(x):
    return float(a2+x*(a1-a2)/(d1-d2))
def l_a_x(a):
    return ma.sin(a)*taille


# Création de la grille avec stockage des points dans des arrays numpy
import numpy as np
#tous les points tous les taille m sur la ligne travaillée
Y_0=np.linspace(1., 1., fact+1) 

for i in range(0,fact+1):
    Y_0[i]=taille*i #depuis x=0 jusqu'à x_max = d1-d2
    
#on calcule les distances donc les écarts successifs
Y=np.linspace(1., 1., fact+1) 
somme=0
for i in range(0,fact+1):
    Y[i]=l_a_x(angle_x(Y_0[i]))
    somme=somme+Y[i]



#on scale les données
s=h_p/somme
for i in range (0,fact+1):
    Y[i]=Y[i]*s/ratio
    
from PIL import Image, ImageTk 
import  tkinter as tk 
root = tk.Tk() 

image = Image.open("25_scale.png") 
photo = ImageTk.PhotoImage(image) 
 
canvas = tk.Canvas(root, width = image.size[0], height = image.size[1]) 
canvas.create_image(0,0, anchor = tk.NW, image=photo)

#paramètre du range à définir en fonction de la taille de l'image
coord_fuite_x=376
param_l=[coord_fuite_x//L1_pix+1,(image.size[0]-coord_fuite_x)//L1_pix+1]
param=15
max_cote=int(max(image.size[0]//L1_pix,image.size[0]//L2_pix))
major_X=np.linspace(1.,1.,max_cote*(fact+1))


for i in range(1,fact+1):
    Y[i]=Y[i]+Y[i-1]

X0=np.linspace(0., 0., fact+1)
   
for i in range(0,fact+1):
    major_X[i]=-L2_5_pix+i*((L2_5_pix-L1_5_pix)/fact)
    for j in range(1,max_cote):
        major_X[j*(fact+1)+i]=j*major_X[i]
#création du vecteur de l'autre côté de la ligne de fuite
major_minus_X=np.copy(major_X)
for i in range(0,len(major_minus_X)):
    major_minus_X[i]=-major_minus_X[i]


#changement de y
donnee_debut=186 #normalement pour autres images on aura pas besoin
Y_image=np.linspace(0.,0., fact+1)
Y_image[0]=donnee_debut
for i in range(1,fact+1):
    Y_image[i]=donnee_debut-Y[i-1] #on rajoute l'écart à chaque fois

#décalage des x avec le point de ligne de fuite

for i in range(0,fact+1):
    X0[i]+=coord_fuite_x
for j in range(0,max_cote*(fact+1)):
    major_X[j]+=coord_fuite_x
    major_minus_X[j]+=coord_fuite_x



#######     prolongement de la grille ##############

#en bas 

Y_bottom=np.linspace(1.,1.,int(d2//taille))
for i in range(0,len(Y_bottom)):
    Y_bottom[i]=l_a_x(angle_x(-taille*i))*s/ratio #-taille*i pour partir dans l'autre sens

for i in range(1,len(Y_bottom)):
    Y_bottom[i]=Y_bottom[i]+Y_bottom[i-1] #de la même manière dans les négatifs

Y_image_bottom=np.linspace(0.,0., int(d2//taille))
Y_image_bottom[0]=donnee_debut
for i in range(1,fact+1):
    Y_image_bottom[i]=donnee_debut+Y_bottom[i-1] #on rajoute l'écart à chaque fois


X0_bottom=np.linspace(0.,0., int(d2//taille))
major_X_bottom=np.linspace(1.,1.,max_cote*(int(d2//taille)))
for i in range(0,int(d2//taille)):
    major_X_bottom[i]=-L2_5_pix-i*((L2_5_pix-L1_5_pix)/fact)
    for j in range(1,max_cote):
        major_X_bottom[j*(int(d2//taille))+i]=j*major_X_bottom[i]
        
for i in range(0,int(d2//taille)):
    X0_bottom[i]+=coord_fuite_x
    
for j in range(0,max_cote*(fact+1)):
    major_X_bottom[j]+=coord_fuite_x
    #major_minus_X[j]+=coord_fuite_x  a faire major_minus_X_bottom
    

############        VISUALTION SUR GRAPHIQUE       ###################



for i in range(0,fact):
    canvas.create_line(X0[i],Y_image[i],X0[i],Y_image[i+1],fill='red')
    canvas.create_line(X0_bottom[i],Y_image_bottom[i],X0_bottom[i],Y_image_bottom[i+1],fill='red')
    #horizontal X0
    canvas.create_line(X0[i],Y_image[i],major_X[i],Y_image[i],fill='blue')
    canvas.create_line(X0_bottom[i],Y_image_bottom[i],major_X_bottom[i],Y_image_bottom[i],fill='blue')
    
    canvas.create_line(X0[i],Y_image[i],major_minus_X[i],Y_image[i],fill='blue')
    if i==fact-1:
        canvas.create_line(X0[i],Y_image[fact],major_X[fact],Y_image[fact],fill='blue')
        canvas.create_line(X0_bottom[i],Y_image_bottom[fact],major_X_bottom[fact],Y_image_bottom[fact],fill='blue')
        
        canvas.create_line(X0[i],Y_image[fact],major_minus_X[fact],Y_image[fact],fill='blue')
       
    for j in range(1,max_cote):
        #vertical
        canvas.create_line(major_X[j*(fact+1)+i],Y_image[i],major_X[j*(fact+1)+i+1],Y_image[i+1],fill='red')
        canvas.create_line(major_X_bottom[j*(fact+1)+i],Y_image_bottom[i],major_X_bottom[j*(fact+1)+i+1],Y_image_bottom[i+1],fill='red')
        
        canvas.create_line(major_minus_X[j*(fact+1)+i],Y_image[i],major_minus_X[j*(fact+1)+i+1],Y_image[i+1],fill='red')
    for j in range(0,max_cote-1):
        #horizontal
        if i==fact-1:
            canvas.create_line(major_X[j*(fact+1)+i+1],Y_image[i+1],major_X[(j+1)*(fact+1)+i+1],Y_image[i+1],fill='blue')
            canvas.create_line(major_X_bottom[j*(fact+1)+i+1],Y_image_bottom[i+1],major_X_bottom[(j+1)*(fact+1)+i+1],Y_image_bottom[i+1],fill='blue')
            
            canvas.create_line(major_minus_X[j*(fact+1)+i+1],Y_image[i+1],major_minus_X[(j+1)*(fact+1)+i+1],Y_image[i+1],fill='blue')
            
        canvas.create_line(major_X[j*(fact+1)+i],Y_image[i],major_X[(j+1)*(fact+1)+i],Y_image[i],fill='blue')
        canvas.create_line(major_X_bottom[j*(fact+1)+i],Y_image_bottom[i],major_X_bottom[(j+1)*(fact+1)+i],Y_image_bottom[i],fill='blue')
        
        canvas.create_line(major_minus_X[j*(fact+1)+i],Y_image[i],major_minus_X[(j+1)*(fact+1)+i],Y_image[i],fill='blue')
            
          

canvas.pack(side=tk.RIGHT)



#création de la détection d'un point,relief

altitude=800


################     FONCTIONS DE L'INTERFACE GRAPHIQUE      ##################


def calcul_pos(alt,y):
    d=alt/ma.tan(angle_x(y))
    ind=0
    for i in range(0,len(Y_image)-1):
        if y>Y_image[i] and y<=Y_image[i+1]:
            ind=i
    dist=d2+ind*taille-d
    print("Intervalle de distance en vertical")
    return (dist/100,dist/100+taille/100)

def calcul_dist(y): #rajouter x pour ensuite le calcul dans R2
    #si on est dans la partie haute de base
    ind=0
    if y<=Y_image_bottom[0]:
        for i in range(0,len(Y_image)-1):
            print(i)
            if y<=Y_image[i] and y>Y_image[i+1]:
                ind=i
                
        dist=d2+taille*ind
        return (dist/100,dist/100+taille/100)
    
    #si on est dans la partie basse construite
    else :
        for i in range(0,len(Y_image_bottom)-1):
            if y>Y_image_bottom[i] and y<=Y_image_bottom[i+1]:
                ind=i
        dist=d2-taille*ind
        return (dist/100-taille/100,dist/100)
            

def clic_gauche(event):
    """ Gestion de l'événement clic gauche sur la zone graphique """
    Y = event.y
    print(calcul_pos(altitude,Y))
    label_1.configure(text=str(calcul_pos(altitude,Y)))
    
def clic_droit(event):
    """ Gestion de l'événement clic droit sur la zone graphique """
    X=event.x
    Y = event.y
    print(calcul_dist(Y))
    label_2.configure(text=str(calcul_dist(Y)), )

canvas.bind('<Button-1>', clic_gauche)
canvas.bind('<Button-3>', clic_droit)
l_1 = tk.LabelFrame(root, text="Position avec considération de l'altitude")
l_2 = tk.LabelFrame(root, text="Position sans considération de l'altitude")
l_1.pack(side = tk.LEFT)
l_2.pack(side = tk.RIGHT)
label_1=tk.Label(l_1, text="position")
label_1.pack()
label_2=tk.Label(l_2, text="position")
label_2.pack()



root.mainloop()
