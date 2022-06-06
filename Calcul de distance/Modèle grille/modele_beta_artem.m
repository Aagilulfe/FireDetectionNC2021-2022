%toutes les données en centimètres (m)
altitude=1066.87;
d1=7729.12;
d2=2362.96;
a1=atan(altitude/d1);
a2=atan(altitude/d2);

L2=216;
L2_reel=179.06;
L1=80;
L1_reel=174.67;

%pour 5m, on fait les transformations :
L2_=216*5/L2;
L1_=80*5/L1;

%transformation en pixels de la différence entre les 2 points
diff=744; 
fact=floor((d1-d2)/((10^2)*5));

% élaboration de la grille
a= @(x) a2+x.*(a1-a2)/(d1-d2);
l= @(a) sin(a).*5;

X=ones(1,fact+1); %tous les points tous les 5 m compris sur la ligne travaillée
for i = 1:fact+1
    X(i)= d2/(10^2) +5*(i-1);
end
disp(X)
%on calcule les distances donc les écarts successifs
Y=l(a(X));
for i = 2:fact+1
    Y(i)=Y(i-1)+Y(i);
end
% Y(1) est au début

s=744/(abs(Y(fact+1)-Y(1)));
for i = 1:fact+1
    Y(i)=(Y(i)-Y(1))*s;
end


X1=ones(1,fact+1);
X2=ones(1,fact+1);
X3=ones(1,fact+1);
X4=ones(1,fact+1);

for i= 1:fact+1
    X1(i)=-L2+i*(L2-L1)/(fact+1);
    X2(i)=2*X1(i);
    X3(i)=3*X1(i);
    X4(i)=4*X1(i);
end



X0=zeros(1,fact+1);

plot(X0,Y,'.')
hold on
plot(X1,Y,'.')
plot(-X1,Y,'.')
plot(X2,Y,'.')
plot(X3,Y,'.')
plot(X4,Y,'.')
xlabel("x")
ylabel("y")
title("Grille 5x5, photo ARTEM")
axis([-2968 0 0 4000])

disp(Y)
disp(X1)







