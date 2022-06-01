%% 1.jpg (affiche Mines)

%carre entier

p_reel=[0, 0, 78.6, 78.6 ; 55.2, 0, 0, 55.2];
p_img=[1025 1127 2044 2139; 2043 1628 1625 2037];

v=homography_solve(p_img,p_reel);
aff_top_left=[1316;1797];

crd_comp=homography_transform(aff_top_left,v)
crd_reel=[17.95;26.2];

erreur_19_03(crd_comp,crd_reel);

% point extérieur, carré
pt_ext=[203;1627];
crd_reel=[-78.6;0];
crd_comp=homography_transform(pt_ext,v)
erreur_19_03(crd_comp,crd_reel);

%quadrilatère quelconque

p_reel=[0 0 46.1 78.6; 55.2 0 14.3 55.2]
p_img=[1025 1127 1676 2139; 2043 1628 1713 2037];

v=homography_solve(p_img,p_reel);
aff_top_left=[1316;1797];

crd_comp=homography_transform(aff_top_left,v)
crd_reel=[17.95;26.2];

erreur_19_03(crd_comp,crd_reel);

%5 points
p_reel=[0 17.95 0 78.6 78.6; 55.2 26.2 0 0 55.2];
p_img=[1025 1316 1127 2044 2139; 2043 1797 1628 1625 2037];

v=homography_solve(p_img,p_reel);
aff_top_right=[1848;1798];

crd_comp=homography_transform(aff_top_right,v)
crd_reel=[60.65;17.95];

erreur_19_03(crd_comp,crd_reel);

%6 points
p_reel=[0 17.95 0 78.6 60.65 78.6; 55.2 26.2 0 0 26.2 55.2];
p_img=[1025 1316 1127 2044 1848 2139; 2043 1797 1628 1625 1798 2037];

v=homography_solve(p_img,p_reel);
t_artem=[1577;1728];

crd_comp=homography_transform(t_artem,v)
crd_reel=[39.3;16.1];

erreur_19_03(crd_comp,crd_reel);

y_nancy=[1676;1713];

crd_comp=homography_transform(y_nancy,v)
crd_reel=[46.1;14.3];

erreur_19_03(crd_comp,crd_reel);


%% Nouvelle Calédonie

%Coordonnées des essais :

%Caméra : -22.306524046942016, 166.76376076850846
%Feu 1 : -22.30348694525021, 166.72494906334308
%Feu 2 & 3 : -22.303621331688806, 166.74214706475448

%25.jpg

% Construction du polygone

% distance en m | angle en °
d1=677 ; a1=15 ; d2=2584; a2=94.67; d3=715; a3=154.34; d4=1955; a4=275;
d=[d1 d2 d3 d4];
a=[a1 a2 a3 a4];
a=a.*(pi/180);
p_reel=zeros(2,5);
for i =1:4
    p_reel(1,i+1)=p_reel(1,i)+d(i)*cos(a(i));
    p_reel(2,i+1)=p_reel(2,i)+d(i)*sin(a(i));
end

plot(p_reel(1,:),p_reel(2,:))

%test
p_img=[936 1034 1272 1298;591 457 460 566];
p_reel=p_reel.*(-1);
plot(p_reel(1,:),p_reel(2,:))

v=homography_solve(p_img,p_reel(:,1:4));
aff_top_left=[1144;507];

crd_comp=homography_transform(aff_top_left,v)
crd_reel=[-583;1319];

erreur_19_03(crd_comp,crd_reel);

%IMG_20220107_150134.jpg

p_img=[1392 1632 2154 2028; 2123 2009 1997 2153];
p_reel=[0 0 21.38 21.45; 30.45 0 0 32.46];
v=homography_solve(p_img,p_reel);

pt_test=[174;2693];
crd_comp=homography_transform(pt_test,v)
crd_reel=[-0.1,82.93];


pt_test_2=[1074;3550];
crd_comp=homography_transform(pt_test_2,v)

