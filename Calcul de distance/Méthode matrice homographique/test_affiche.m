pin= [0, 0, 78.6, 78.6 ; 35.2, 0, 0, 35.2];
% image 1
L1=921; %pixels
L2=1117;
l1=423;
l2=412;
ecart_orgn=90;
pout=[0,ecart_orgn, (L1+ ecart_orgn), L2 ; l1, 0, 0, l2];

%test sens 1
v=homography_solve(pin,pout)
point=[246;216];

y=homography_transform(point,v)

%test sens 2
v=homography_solve(pout,pin)
point=[246;216];

y=homography_transform(point,v)
%marche good dans ce sens

% test trapèze
decal_l=218;
decal_r=214;

pin= [0, 18.5, 78.6-18.5, 78.6 ; 35.2, 0, 0, 35.2];
pout =[0,ecart_orgn+decal_l, (L1+ ecart_orgn)-decal_r, L2 ; l1, 0, 0, l2];
v=homography_solve(pout,pin);
y=homography_transform(point,v)

p_out=[-246;-216];
y_out=homography_transform(p_out,v)

%test losange
%dimensions affiche
hauteur=29;
longueur=42.7;
deltah_y=11.9;
decal_droite_y=32.5;
deltah_t=10.1;
decal_droite_t=40;

pout =[566,246, 505, 804 ; 411, 277, 166, 277];
pin=[(78.6)/2,(78.6-longueur)/2,(78.6)/2,(78.6-longueur)/2;55.2,55.2-hauteur/2,55.2-hauteur,55.2-hauteur/2 ]
v=homography_solve(pout,pin);
y=homography_transform(point,v)

