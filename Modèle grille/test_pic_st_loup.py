# -*- coding: utf-8 -*-
import math as ma

###############         DONNEES       #############################


taille=10000
ratio=4
#toutes les données en centimètres (m)
altitude=(609-170)*10**2 #à modifier le 18
d1_prev=234840
d2=101703
a1=ma.atan(altitude/d1_prev)
a2=ma.atan(altitude/d2)
#altitude des points de référence
h1=213*10**2
h2=170*10**2

dh=h1-h2
d1=d1_prev+dh/(ma.tan(a1))

#longueurs de référence
L2_pix=384 #pixels
L2_reel=14415 #centimètres
L1_pix=248 #pixels
L1_reel_prev=31921 #centimètres

#calcul de L1_reel
lp=d1_prev/(ma.cos(a1))
ll=d1/(ma.cos(a1))
L1_reel=L1_reel_prev*ll/lp

#pour taille m, on fait les transformations (pour l'équivalent en pixels):
L2_5_pix=L2_pix*taille/L2_reel
L1_5_pix=L1_pix*taille/L1_reel


#plage de pixels sur laquelle on fait le modèle
h_p=716 #mesure à prendre sur la photo non scale
donnee_debut=1980 #normalement pour autres images on aura pas besoin

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

image = Image.open("pic_4_scaled.png") 
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
print(Y)

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

# =============================================================================
# Y_bottom=np.linspace(1.,1.,int(d2//taille))
# for i in range(0,len(Y_bottom)):
#     Y_bottom[i]=l_a_x(angle_x(-taille*i))*s/ratio #-taille*i pour partir dans l'autre sens
# print(Y_bottom)
# for i in range(1,len(Y_bottom)):
#     Y_bottom[i]=Y_bottom[i]+Y_bottom[i-1] #de la même manière dans les négatifs
# print(Y_bottom)
# Y_image_bottom=np.linspace(0.,0., int(d2//taille))
# Y_image_bottom[0]=donnee_debut
# for i in range(1,fact+1):
#     Y_image_bottom[i]=donnee_debut+Y_bottom[i-1] #on rajoute l'écart à chaque fois
# 
# 
# X0_bottom=np.linspace(0.,0., int(d2//taille))
# major_X_bottom=np.linspace(1.,1.,max_cote*(int(d2//taille)))
# for i in range(0,int(d2//taille)):
#     major_X_bottom[i]=-L2_5_pix-i*((L2_5_pix-L1_5_pix)/fact)
#     for j in range(1,max_cote):
#         major_X_bottom[j*(int(d2//taille))+i]=j*major_X_bottom[i]
#         
# for i in range(0,int(d2//taille)):
#     X0_bottom[i]+=coord_fuite_x
#     
# for j in range(0,max_cote*(fact+1)):
#     major_X_bottom[j]+=coord_fuite_x
#     #major_minus_X[j]+=coord_fuite_x  a faire major_minus_X_bottom
# =============================================================================
    


########      grille sur le canvas   #############
for i in range(0,fact):
    canvas.create_line(X0[i],Y_image[i],X0[i],Y_image[i+1],fill='red')
    #canvas.create_line(X0_bottom[i],Y_image_bottom[i],X0_bottom[i],Y_image_bottom[i+1],fill='red')
    #horizontal X0
    canvas.create_line(X0[i],Y_image[i],major_X[i],Y_image[i],fill='blue')
    #canvas.create_line(X0_bottom[i],Y_image_bottom[i],major_X_bottom[i],Y_image_bottom[i],fill='blue')
    
    canvas.create_line(X0[i],Y_image[i],major_minus_X[i],Y_image[i],fill='blue')
    if i==fact-1:
        canvas.create_line(X0[i],Y_image[fact],major_X[fact],Y_image[fact],fill='blue')
        #canvas.create_line(X0_bottom[i],Y_image_bottom[fact],major_X_bottom[fact],Y_image_bottom[fact],fill='blue')
        
        canvas.create_line(X0[i],Y_image[fact],major_minus_X[fact],Y_image[fact],fill='blue')
       
    for j in range(1,max_cote):
        #vertical
        canvas.create_line(major_X[j*(fact+1)+i],Y_image[i],major_X[j*(fact+1)+i+1],Y_image[i+1],fill='red')
        #canvas.create_line(major_X_bottom[j*(fact+1)+i],Y_image_bottom[i],major_X_bottom[j*(fact+1)+i+1],Y_image_bottom[i+1],fill='red')
        
        canvas.create_line(major_minus_X[j*(fact+1)+i],Y_image[i],major_minus_X[j*(fact+1)+i+1],Y_image[i+1],fill='red')
    for j in range(0,max_cote-1):
        #horizontal
        if i==fact-1:
            canvas.create_line(major_X[j*(fact+1)+i+1],Y_image[i+1],major_X[(j+1)*(fact+1)+i+1],Y_image[i+1],fill='blue')
            #canvas.create_line(major_X_bottom[j*(fact+1)+i+1],Y_image_bottom[i+1],major_X_bottom[(j+1)*(fact+1)+i+1],Y_image_bottom[i+1],fill='blue')
            
            canvas.create_line(major_minus_X[j*(fact+1)+i+1],Y_image[i+1],major_minus_X[(j+1)*(fact+1)+i+1],Y_image[i+1],fill='blue')
            
        canvas.create_line(major_X[j*(fact+1)+i],Y_image[i],major_X[(j+1)*(fact+1)+i],Y_image[i],fill='blue')
        #canvas.create_line(major_X_bottom[j*(fact+1)+i],Y_image_bottom[i],major_X_bottom[(j+1)*(fact+1)+i],Y_image_bottom[i],fill='blue')
        
        canvas.create_line(major_minus_X[j*(fact+1)+i],Y_image[i],major_minus_X[(j+1)*(fact+1)+i],Y_image[i],fill='blue')
            
          

canvas.pack(side=tk.RIGHT)


################     FONCTIONS DE L'INTERFACE GRAPHIQUE      ##################


#création de la détection d'un point,relief

alt=(261-170)*10**2

def calcul_with_alt(alt,y,x):
    ind_y=0
    ind_x=0
    cote=""
    for i in range(len(Y_image)-1):
        if y>=Y_image[i] and y<Y_image[i+1]:
            ind_y=i
    
    d_moins_min=alt*(d2+ind_y*taille)/altitude
    d_moins_max=alt*(d2+(ind_y+1)*taille)/altitude
    
    d=d2+ind_y*taille-d_moins_min
    ind_y_reel=int((d-d2)//taille)
    
    for i in range(0,fact):
        if x<donnee_debut:  #on regarde de quel côté on est pour avoir moins de test à faire
            if x>=major_X[ind_y_reel +i] and x<major_X[ind_y_reel+i+1]:
                ind_x=i
                cote="neg"
        else:            
            if x>=major_minus_X[ind_y_reel+i] and x<major_minus_X[ind_y_reel+i+1]:
                ind_x=i
                cote="pos"
    if cote=="pos":
        IC_x=(ind_x*taille,(ind_x+1)*taille)
    else:
        IC_x=(-ind_x*taille,-(ind_x+1)*taille)
    
    IC_y=(int(d2+ind_y*taille-d_moins_min),int(d2+ind_y*taille-d_moins_max))
    return ("IC_y",IC_y,"IC_x",IC_x)
    
        
def calcul_without_alt(x,y):
    ind_x=0
    ind_y=0
    for i in range(len(Y_image)-1):
        if y>=Y_image[i] and y<Y_image[i+1]:
            ind_y=i
    d_y=ind_y*taille+d2
    IC_y=(d_y,d_y+taille)
    
    for i in range(0,fact):
        if x<donnee_debut:  #on regarde de quel côté on est pour avoir moins de test à faire
            if x>=major_X[ind_y +i] and x<major_X[ind_y+i+1]:
                ind_x=i
                cote="neg"
        else:            
            if x>=major_minus_X[ind_y+i] and x<major_minus_X[ind_y+i+1]:
                ind_x=i
                cote="pos"
    if cote=="pos":
        IC_x=(ind_x*taille,(ind_x+1)*taille)
    else:
        IC_x=(-ind_x*taille,-(ind_x+1)*taille)
    
    return ("IC_y",IC_y,"IC_x",IC_x)        
        


def clic_gauche(event):
    """ Gestion de l'événement clic gauche sur la zone graphique """
    Y = event.y
    X=event.x
    print(calcul_with_alt(alt,Y,X))
    label_1.configure(text=str(calcul_with_alt(alt,Y,X)))
    
def clic_droit(event):
    """ Gestion de l'événement clic droit sur la zone graphique """
    X=event.x
    Y = event.y
    label_2.configure(text=str(calcul_without_alt(X,Y)))
    


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
