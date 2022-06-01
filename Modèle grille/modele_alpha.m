a1=pi/6;
a2=pi/4;
a= @(x) a2+x.*(a1-a2);
l= @(a) sin(a).*5;
X=linspace(0,1,10);
X2=ones(1,10);
Y=l(a(X));
plot(X2,Y,'.')
hold on

d_52=5;
d_51=4;
X1=ones(1,10);
for i= 1:10
    X1(i)=0.9-0.1*i/10;
end

plot(X1,Y,'.')
disp(Y)
