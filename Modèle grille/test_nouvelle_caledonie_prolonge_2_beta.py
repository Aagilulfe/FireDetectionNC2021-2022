# -*- coding: utf-8 -*-
import math as ma
import numpy as np
from PIL import Image, ImageTk 
import  tkinter as tk 

#########   Création interface graphique  ################
root = tk.Tk()
image = Image.open("25_scale.png") 
photo = ImageTk.PhotoImage(image)  
canvas = tk.Canvas(root, width = image.size[0], height = image.size[1]) 
canvas.create_image(0,0, anchor = tk.NW, image=photo)


##################   Données ##################

taille=25000
ratio=3
#toutes les données en centimètres (m)
altitude=(315-18)*10**2
d1=404989
#y_pix_1 = 
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

print(L2_5_pix)
print(L1_5_pix)

#plage de pixels sur laquelle on fait le modèle
h_p=90
#points à corriger
#rajout de 1 dans ce cas pour corriger
fact=abs(int((d1-d2)/taille)) #pour savoir combien de points en vertical on va faire (avant de prolonger la grille)

coord_fuite_x=376
###################################################


class zone:
    
    def __init__(self,x1,y1,x2,y2,x3,y3,x4,y4):
        #bas --> droite --> haut --> gauche
        self.y_b=y1 #c'est aussi y2
        self.y_t=y3
        self.x_b_l=x1
        self.x_b_r=x2
        self.x_t_r=x3
        self.x_t_l=x4
    
    def draw(self):
        pts=[(self.x_b_l,self.y_b),(self.x_b_r,self.y_b),(self.x_t_r,self.y_t),(self.x_t_l,self.y_t)]
        canvas.create_polygon(pts,fill='', outline="red", activefill="magenta")
    
    


###################################################

#### définition de la matrice ######
Stock=np.zeros
#définir le vecteur X0 jusqu'au bout
#regarder combien vaut X1 au bout
#multiplier pour que ça couvre toute la zone
#calculer ensuite



#fonctions pour le calcul
def angle_x(x):
    return float(a2+x*(a1-a2)/(d1-d2))
def l_a_x(a):
    return ma.sin(a)*taille

########   Y    #########
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

for i in range(1,fact+1):
    Y[i]=Y[i]+Y[i-1]
    
print("Y",Y)
#######  Y_haut #########
limite= 1000000   # à modifier
fact_haut=int(limite/taille)
Y_haut=np.linspace(1.,1.,fact_haut)
for i in range(0,fact_haut):
    
    if l_a_x(angle_x(taille*(i+fact+1)))>0:
        Y_haut[i]=taille*(i+fact+1) #à partir de fact
        Y_haut[i]=l_a_x(angle_x(Y_haut[i]))
        Y_haut[i]=Y_haut[i]*s/ratio
        if i==0:
            Y_haut[i]+=Y[fact] #on démarre à partir de la fin du Y normal
        else :
            Y_haut[i]=Y_haut[i]+Y_haut[i-1] 
    else :
        Y_haut[i]=0
        
print("Y_haut",Y_haut)

    
#######  Y_bas ##########

#♠limite bas à définir
fact_bas=3*fact
Y_bas=np.linspace(1. , 1., fact_bas)  #6*fact limite provisoire
for i in range(0,fact_bas):
    Y_bas[i]=-taille*(i+1) #à partir de fact mais dans sens inverse
    Y_bas[i]=l_a_x(angle_x(Y_bas[i]))
    Y_bas[i]=Y_bas[i]*s/ratio
    if i>0:
        Y_bas[i]=Y_bas[i]+Y_bas[i-1] #on démarre dans l'autre sens
    
print("Y_bas",Y_bas)

Y_concat=np.concatenate((Y_bas,Y,Y_haut))

donnee_debut=186
Y_image_concat=np.linspace(1.,1.,fact+1+fact_bas+fact_haut+1)
Y_image_concat[fact_bas]=donnee_debut #origine des Y
for i in range(0,fact_bas):
    Y_image_concat[fact_bas-i-1]=donnee_debut+Y_bas[i]
for i in range(0,fact+1): #on enlève fact_bas+1
    Y_image_concat[fact_bas+1+i]=donnee_debut-Y[i]
for i in range(0,fact_haut):
    Y_image_concat[fact_bas+fact+1+i+1]=donnee_debut-Y_haut[i]
    

############  major_x ###################

#limite max_x à redéfinir, car peut être linéarité de la profondeur pas optimale
#il faudrait également que je vérifie que les points sont bien pris à la même altitude, sinon affiner le modèle
i=0
while L2_5_pix+(L1_5_pix-L2_5_pix)*i/fact>0:
    i+=1
max_x=int(image.size[0]//2*((L2_5_pix+(L1_5_pix-L2_5_pix)*(i-1)/fact)))

major_X=np.zeros((fact+1+fact_bas+fact_haut+1,max_x+1))  #max_x +1 pour avoir la ligne de 0
for j in range(1,max_x+1):
    for i in range(0,fact+1+fact_bas+fact_haut+1):
        major_X[i][j]=L2_5_pix+(-fact_bas+i)*(L1_5_pix-L2_5_pix)
        major_X[i][j]=j*major_X[i][j]

############  minus_X ###################

minor_X=np.copy(major_X)
for i in range(0,len(minor_X)):
    for j in range(0,len(minor_X[0])):
        minor_X[i][j]=-minor_X[i][j]
        
############ Décalage par rapport au point de fuite  ##############

for i in range(0,len(minor_X)):
    for j in range(0,len(minor_X[0])):
        major_X[i][j]+=coord_fuite_x
        minor_X[i][j]+=coord_fuite_x

######### Création de la grille  ###################

M_major=[["" for i in range(0,max_x)]for i in range(0,len(Y_image_concat)-1)]
M_minor=[["" for i in range(0,max_x)]for i in range(0,len(Y_image_concat)-1)]


for i in range(0,len(Y_image_concat)-1):
    for j in range(0,max_x):
        M_major[i][j]=zone(major_X[i][j],Y_image_concat[i],major_X[i][j+1],Y_image_concat[i],major_X[i+1][j+1],Y_image_concat[i+1],major_X[i+1][j],Y_image_concat[i+1])
        M_major[i][j].draw()
        
        # M_minor[i][j]=zone(minor_X[i][j],Y_image_concat[i],minor_X[i][j+1],Y_image_concat[i],minor_X[i+1][j+1],Y_image_concat[i+1],minor_X[i+1][j],Y_image_concat[i+1])
        # M_minor[i][j].draw()



canvas.pack(side=tk.RIGHT)



#création de la détection d'un point,relief
    

def clic_gauche(event):
    """ Gestion de l'événement clic gauche sur la zone graphique """
    X=event.x
    Y = event.y
    L=canvas.find_closest(X, Y)
    label_1.configure(text=str(L))
    
def clic_droit(event):
    """ Gestion de l'événement clic droit sur la zone graphique """
    X=event.x
    Y = event.y

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
