import numpy  as np
x= np.array([-5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0]) 
yexp= np.array([-1207.0, -624.0, -263.0, -70.0, 9.0, 28.0, 41.0, 102.0, 265.0, 584.0]) 
def func(a):
	y = a[0]*x*x* x + a[1]*x*x + a[2]*x + a[3]
	erro = y - yexp
	return np.array(sum(erro * erro) / len(yexp)), y
