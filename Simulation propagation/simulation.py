
from copy import deepcopy
import random
import math


from tkinter import *


# convention : hauteur largeur

# la class zone représente une zone de la grille, elle a différentes caractéristiques en fonction
# de sa quantité de conbustible : fuel, de sa position (x,y) et de son état brulé, en train de bruler, etc...
class zone:
    def __init__(self, altitude, fuel, y, x) -> None:
        self.enFeu = False
        self.fireState = 0  # 0:None 1:évaporation 2:pyrolyse 3:flame 4:down
        self.consumed = 0  # pourcentage
        self.fuel: int = fuel  # entre 100 et 200

        self.fireDrawn = False
        self.burned = False
        self.burnedDrawn = False
        self.altitude = altitude

        self.y = y
        self.x = x

    # renvoie la probabilité de bruler une zone adjacente en fonction des paramètres
    # c'est ici qu'on peut faire intervenir les paramètres de la zone
    # on peut également faire intervenir les paramètres des zones adjacentes
    def getP(self, p, zone_adjacente=None):
        if self.consumed >= self.fuel:
            return 0
        if self.consumed < 20:
            return 0
        if self.consumed < 50:
            return p*1.5
        return p*2

    # renvoie la probabilité que la zone s'éteigne en fonction des paramètres
    def getPdown(self):
        if self.consumed < 20:
            return 0.1
        if self.consumed < 50:
            return 0.05
        return 0

    # évolution de la zone en fonction de son état
    def update(self):
        temp = self.fireState
        if self.consumed < 20:
            self.fireState = 1
            self.consumed += 10
            return
        if 20 <= self.consumed < 50:
            self.fireState = 2
            self.consumed += 20
            if temp-self.fireState != 0:
                self.fireDrawn = False
            return
        if 50 <= self.consumed < self.fuel:
            self.fireState = 3
            self.consumed += 30
            if temp-self.fireState != 0:
                self.fireDrawn = False
            return
        if self.consumed >= self.fuel:
            self.fireState = 4
            self.burned = True
            if temp-self.fireState != 0:
                self.fireDrawn = False
            return


class simulation:

    # initialisation de la simulation
    def __init__(self, L, heigth, width, maillage,nb_iter,speed,Vx=None,Vy=None) -> None:

        self.vfixed=False
        if Vx!=None and Vy!=None:
            self.Vx = Vx
            self.Vy = Vy
            self.vfixed=True
        else:
            self.Vx = random.randint(0, 60)*random.choice([-1, 1])
            self.Vy = random.randint(0, 60)*random.choice([-1, 1])

    
        self.Vmax = 60

        self.case_vent = 100
        self.LongeurZone = L

        self.heigth = 600
        self.width = int(600*width/heigth)
        self.L = int(self.width/(width))

        self.maillage = maillage
        self.Y = heigth
        self.X = width

        self.speedcoef = speed
        self.speed = round(1000/self.speedcoef)
        self.time = 0

        self.Vf = 2.5
        self.p = self.Vf*self.speed*self.speedcoef/(1000*self.LongeurZone)

        self.root = Tk()

        self.ax = 1
        self.ay = 1
        self.nb_iter = nb_iter

        self.initmatrice(self.Y//2, self.X//2)

        self.initTk()

    # création des zones
    def initmatrice(self, y, x):
        self.zoneEnFeu = []
        if self.maillage == []:
            self.matrice = []
            for k in range(self.Y):
                L = []
                for n in range(self.X):
                    z = zone(random.choice([-1, 0, 0, 1]),
                             random.randint(200, 300), k, n)
                    L.append(z)
                self.matrice.append(L)
        else:
            self.matrice = deepcopy(self.maillage)
        self.matrice[y][x].enFeu = True
        self.matrice[y][x].fireState = 1
        self.zoneEnFeu.append(self.matrice[y][x])

    # change la probabilité de base de propagation en fonction de la vitesse du vent
    def changeVent(self):
        coef_up = 1
        coef_down = 0.05
        # update des coefficients pour éviter une trop forte propagtion dans le sens contraire du vent
        if self.Vx > 0:
            self.alphaEstOuest = coef_down
            self.alphaOuestEst = coef_up
        else:
            self.alphaOuestEst = coef_down
            self.alphaEstOuest = coef_up
        if self.Vy > 0:
            self.alphaSudNord = coef_down
            self.alphaNordSud = coef_up
        else:
            self.alphaNordSud = coef_down
            self.alphaSudNord = coef_up
        V = self.normeVent()
        self.Vf = V*0.03
        # formule générale de la probabilité de propagation pour rendre compte de la vitesse de propagation
        # du feu environ égale à 3% de la vitesse du vent
        self.p = self.Vf*self.speed*self.speedcoef/(1000*self.LongeurZone)

        # calcul de la probabilité de propagation en fonction de la vitesse du vent + biais de propagation
        self.px = 0.03*abs(self.Vx)*self.speed * \
            self.speedcoef/(1000*self.LongeurZone)+0.01
        self.py = 0.03*abs(self.Vy)*self.speed * \
            self.speedcoef/(1000*self.LongeurZone)+0.01

    # norme du vent
    def normeVent(self):
        return(math.sqrt(self.Vx*self.Vx+self.Vy*self.Vy))

    # le feu se propage mieux dans les montées que dans les descentes
    def coefAltitude(self, a: zone, b: zone):
        if a.altitude-b.altitude > 0:
            return 0.8
        if a.altitude-b.altitude < 0:
            return 1.2
        return 1

    # coef final de base de propagation
    def coefP(self, y, x, _y, _x):
        coef = 1
        if _x == 1:
            coef *= self.alphaOuestEst
        if _x == -1:
            coef *= self.alphaEstOuest
        if _y == 1:
            coef *= self.alphaNordSud
        if _y == -1:
            coef *= self.alphaSudNord
        coef *= self.coefAltitude(self.matrice[y][x], self.matrice[y+_y][x+_x])
        return coef

    # une étape de temps de la simulation

    def update(self):
        self.time += self.speed*self.speedcoef/1000
        self.labtime.config(text=str(self.time)+" s")
        to_pop = []
        if len(self.zoneEnFeu) == 0:
            self.stop()
        # on parcourt chaque zone en feu car se sont elles qui propagent
        for k in range(len(self.zoneEnFeu)):
            z = self.zoneEnFeu[k]
            y = z.y
            x = z.x
            current_zone: zone = self.matrice[y][x]
            px = current_zone.getP(self.px)
            py = current_zone.getP(self.py)
            current_zone.update()
            self.dessineFeu(y, x)
            # on parcourt les 4 zones adjacentes
            if not current_zone.burned:
                if x < self.Y-1:
                    if not self.matrice[y][x+1].enFeu:
                        nombre_aleat_case_voisine = random.randint(0, 100)
                        if nombre_aleat_case_voisine < self.coefP(y, x, 0, 1)*px*100:
                            self.matrice[y][x+1].enFeu = True
                            self.matrice[y][x+1].fireState = 1
                            self.zoneEnFeu.append(self.matrice[y][x+1])

                if x > 0:
                    if not self.matrice[y][x-1].enFeu:
                        nombre_aleat_case_voisine = random.randint(0, 100)
                        if nombre_aleat_case_voisine < self.coefP(y, x, 0, -1)*px*100:
                            self.matrice[y][x-1].enFeu = True
                            self.matrice[y][x-1].fireState = 1
                            self.zoneEnFeu.append(self.matrice[y][x-1])

                if y < self.Y-1:
                    if not self.matrice[y+1][x].enFeu:
                        nombre_aleat_case_voisine = random.randint(0, 100)
                        if nombre_aleat_case_voisine < self.coefP(y, x, 1, 0)*py*100:
                            self.matrice[y+1][x].enFeu = True
                            self.matrice[y+1][x].fireState = 1
                            self.zoneEnFeu.append(self.matrice[y+1][x])
                if y > 0:
                    if not self.matrice[y-1][x].enFeu:
                        nombre_aleat_case_voisine = random.randint(0, 100)
                        if nombre_aleat_case_voisine < self.coefP(y, x, -1, 0)*py*100:
                            self.matrice[y-1][x].enFeu = True
                            self.matrice[y-1][x].fireState = 1
                            self.zoneEnFeu.append(self.matrice[y-1][x])

                if random.randint(0, 100) < current_zone.getPdown():
                    current_zone.fireState = 0
                    current_zone.enFeu = False
                    to_pop.append(k)
            else:
                to_pop.append(k)
                self.dessineBurned(y, x)
        # on supprime les zones qui ont été éteintes
        to_pop.sort(reverse=True)
        for k in to_pop:
            self.zoneEnFeu.pop(k)

    # réalise 100 simulations et moyenne le résultat
    def monte_carlo(self):
        self.stop()
        self.changeVent()
        self.dessineVent()
        finalmap = []
        for k in range(self.Y):
            L = [0]*self.X
            finalmap.append(L)
        self.initmatrice(self.Y//2, self.X//2)
        matricecopy = deepcopy(self.matrice)
        zoneenfeucopy = deepcopy(self.zoneEnFeu)
        for q in range(self.nb_iter):
            self.matrice = deepcopy(matricecopy)
            self.zoneEnFeu = deepcopy(zoneenfeucopy)
            while len(self.zoneEnFeu) != 0:
                to_pop = []
                for k in range(len(self.zoneEnFeu)):
                    z = self.zoneEnFeu[k]
                    y = z.y
                    x = z.x
                    current_zone: zone = self.matrice[y][x]
                    px = current_zone.getP(self.px)
                    py = current_zone.getP(self.py)

                    current_zone.update()
                    self.dessineFeu(y, x)
                    if not current_zone.burned:
                        if x < self.X-1:
                            if not self.matrice[y][x+1].enFeu:
                                nombre_aleat_case_voisine = random.randint(
                                    0, 100)
                                if nombre_aleat_case_voisine < self.coefP(y, x, 0, 1)*px*100:
                                    self.matrice[y][x+1].enFeu = True
                                    self.matrice[y][x+1].fireState = 1
                                    self.zoneEnFeu.append(self.matrice[y][x+1])

                        if x > 0:
                            if not self.matrice[y][x-1].enFeu:
                                nombre_aleat_case_voisine = random.randint(
                                    0, 100)
                                if nombre_aleat_case_voisine < self.coefP(y, x, 0, -1)*px*100:
                                    self.matrice[y][x-1].enFeu = True
                                    self.matrice[y][x-1].fireState = 1
                                    self.zoneEnFeu.append(self.matrice[y][x-1])

                        if y < self.Y-1:
                            if not self.matrice[y+1][x].enFeu:
                                nombre_aleat_case_voisine = random.randint(
                                    0, 100)
                                if nombre_aleat_case_voisine < self.coefP(y, x, 1, 0)*py*100:
                                    self.matrice[y+1][x].enFeu = True
                                    self.matrice[y+1][x].fireState = 1
                                    self.zoneEnFeu.append(self.matrice[y+1][x])
                        if y > 0:
                            if not self.matrice[y-1][x].enFeu:
                                nombre_aleat_case_voisine = random.randint(
                                    0, 100)
                                if nombre_aleat_case_voisine < self.coefP(y, x, -1, 0)*py*100:
                                    self.matrice[y-1][x].enFeu = True
                                    self.matrice[y-1][x].fireState = 1
                                    self.zoneEnFeu.append(self.matrice[y-1][x])
                        if random.randint(0, 100) < current_zone.getPdown():
                            current_zone.fireState = 0
                            current_zone.enFeu = False
                            to_pop.append(k)
                    else:
                        to_pop.append(k)
                        finalmap[y][x] += 1
                to_pop.sort(reverse=True)
                for k in to_pop:
                    self.zoneEnFeu.pop(k)
        # calcul de la carte finale moyennée
        min = finalmap[0][0]
        max = finalmap[0][0]
        for x in range(self.X):
            for y in range(self.Y):
                if finalmap[y][x] < min and finalmap[y][x] != 0:
                    min = finalmap[y][x]
                if finalmap[y][x] > max:
                    max = finalmap[y][x]
        # normalize finalmap
        if (max-min) != 0:
            for x in range(self.X):
                for y in range(self.Y):
                    finalmap[y][x] = abs((finalmap[y][x]-min)/(max-min))
                    if finalmap[y][x] != 0:
                        self.create_circle(
                            y, x, "#"+hex(int(0xFFFF00-0x00FF00*finalmap[y][x]))[2:])

    # gestion des dessins et de tkinter :

    def create_circle(self, y, x, color):
        x0 = (x+0.5)*self.L - self.L//2*0.90+self.offset
        y0 = (y+0.5)*self.L - self.L//2*0.90+self.offset
        x1 = (x+0.5)*self.L + self.L//2*0.90+self.offset
        y1 = (y+0.5)*self.L + self.L//2*0.90+self.offset
        self.canvas.create_oval(x0, y0, x1, y1, outline="black", fill=color)

    def dessineBurned(self, i, j):
        if not self.matrice[i][j].burnedDrawn:
            self.create_circle(i, j, "black")
            self.matrice[i][j].burnedDrawn = True
            self.matrice[i][j].fireState = 4

    def dessineFeu(self, y, x):
        z: zone = self.matrice[y][x]
        if not z.fireDrawn:
            match z.fireState:
                case 1: self.create_circle(y, x, "yellow")
                case 2: self.create_circle(y, x, "orange")
                case 3: self.create_circle(y, x, "red")

            z.fireDrawn = True

    def dessineVent(self):
        self.cv.delete("all")
        self.lab.config(text="Vx ="+str(round(self.Vx*10) /
                        10)+", Vy="+str(round(self.Vy*10)/10))
        cos = self.Vx/self.normeVent()
        sin = self.Vy/self.normeVent()
        taille = self.case_vent

        self.cv.create_line((taille//2-int(cos*taille/3), taille//2-int(sin*taille/3)), (taille//2+int(cos*taille/3), int(sin*taille/3) + taille//2),
                            fill="black", width=5, smooth=True,
                            arrow="last", arrowshape=(30, 45, 15))

    def initTk(self):
        self.offset = 50
        taille = self.case_vent
        self.next = Button(self.root, text="Next Step", command=self.render)
        self.next.pack(side=LEFT)

        self.canvas = Canvas(self.root, width=self.width+2*self.offset,
                             height=self.heigth+2*self.offset, background="white")
        self.cv = Canvas(self.root, width=taille,
                         height=taille, background="blue")
        self.cv.pack(side=RIGHT)
        self.lab = Label(self.root, text="Vx =" +
                         str(self.Vx)+", Vy="+str(self.Vy))

        self.labtime = Label(self.root, text=str(self.time)+" s")
        self.labtime.pack(side=LEFT)
        self.lab.pack(side=RIGHT)
        self.canvas.pack()
        self.quit_but = Button(self.root, text='Quitter',
                               command=self.root.destroy)
        self.step_but = Button(self.root, text='Start', command=self.start)
        self.restart_but = Button(
            self.root, text='Restart', command=self.restart)
        self.stop_but = Button(
            self.root, text='Stop', command=self.stop)
        self.mc_but = Button(
            self.root, text='Monte Carlo', command=self.monte_carlo)
        self.mc_but.pack(side=LEFT)
        self.step_but.pack(side=LEFT)
        self.quit_but.pack(side=LEFT)
        self.restart_but.pack(side=LEFT)
        self.stop_but.pack(side=LEFT)

        self.changeVent()
        self.dessineVent()

        for y in range(self.Y):
            for x in range(self.X):
                if self.matrice[y][x].fuel > 250:
                    self.create_circle(y, x, "#083B32")
                else:
                    self.create_circle(y, x, "green")
                # self.canvas.create_text(
                #     x*self.L+self.offset, y*self.L+self.offset, text=str(self.matrice[y][x].altitude))

        self.root.mainloop()

    def restart(self):
        self.cv.delete("all")
        self.canvas.delete("all")
        self.initmatrice(self.Y//2, self.X//2)
        if not self.vfixed:
            self.Vx = random.randint(0, 60)*random.choice([-1, 1])
            self.Vy = random.randint(0, 60)*random.choice([-1, 1])
        self.time = 0
        self.changeVent()
        self.dessineVent()

        for y in range(self.Y):
            for x in range(self.X):
                if self.matrice[y][x].fuel > 250:
                    self.create_circle(y, x, "#083B32")
                else:
                    self.create_circle(y, x, "green")
                # self.canvas.create_text(
                #     x*self.L+self.offset, y*self.L+self.offset, text=str(self.matrice[y][x].altitude))

    def start(self):
        self.play = True
        self.run()

    def stop(self):
        self.play = False

    def run(self):
        if self.play:
            self.render()
            self.canvas.after(self.speed, self.run)

    def render(self):
        for k in range(len(self.zoneEnFeu)):
            self.dessineFeu(self.zoneEnFeu[k].y, self.zoneEnFeu[k].x)
        self.changeVent()
        self.dessineVent()
        self.update()


#simulation(25, 600, 600, [])
