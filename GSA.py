import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import math
import random
from tkinter import messagebox
import tkinter as tk

class gsa_py:
    def __init__(self,qA,qT,qV,To):
        self.qA = np.array(qA,dtype='float64')
        self.qT = np.array(qT,dtype='float64')
        self.qV = np.array(qV,dtype='float64')
        self.To = np.array(To,dtype='float64')
        self.XMin = []
        self.func_Min = 0.0
        self.func_conv = {'x':[],'y':[]}
        self.func_conv_min = {'x':[],'y':[]}

    def GSAini(self):
        D = 0
        Pi = np.pi
        # Acceptance probability
        qA1 = self.qA - 1.0
        # Temperature
        qT1 = self.qT - 1.0
        Tqt = self.To * (2.0E0 ** qT1 - 1.0)
        # Visiting Probability
        qV1 = self.qV - 1.0
        exp1 = 2.0E0 / (3.0 - self.qV)
        exp2 = 1.0 / qV1 + 0.5E0 * D - 0.5E0
        if D == 0:
            coef = 1.0
        else:
            gammaUp = math.gamma(exp2)
            gammaDown = math.gamma(1.0 / qV1 - 0.5)
            coef = (qV1 / Pi) ** (D * 0.5) * gammaUp / gammaDown
        return D, qA1, qT1, qV1, Tqt, coef, exp1, exp2

    def Temperature(self,Tqt,qT1):
        def Temperature(t):
            return Tqt / ((1.0 + t) ** qT1 - 1.0)
        return Temperature

    def Delta_X(self,D,coef,qV1,exp1,exp2):
        def Delta_X(T):
            Tup = T ** (D / (self.qT - 3.0))
            R = random.random()
            DeltaX = coef * Tup / ( 1.0 + qV1 * R * R / T ** exp1) ** exp2
            DeltaX *= random.choice([-1, 1])
            return DeltaX
        return Delta_X

    def VarLock(self,lock,X_ini):
        def VarLock(X_t):
            for n in range(len(lock)):
                if lock[n]: X_t[n] = X_ini[n]
            return X_t
        return VarLock

    def plot_convergence(self,t):
        self.func_conv['x'].append(t)
        self.func_conv['y'].append(self.func_Min)
        self.func_conv_min['x'].append(t)
        self.func_conv_min['y'].append(self.func_Min)
        plt.ion()
        fig1, (ax1, ax2) = plt.subplots(2, 1)
        plt.subplots_adjust(hspace=0.8)
        ax1.plot(self.func_conv['x'],self.func_conv['y'], label='Convergence X_t')
        ax1.set_title('Convergence X_t')
        ax1.set(xlabel="NCycles", ylabel='Chi-Square')
        ax2.plot(self.func_conv_min['x'], self.func_conv_min['y'], label='Convergence X_Min')
        ax2.set_title('Convergence X_Min')
        ax2.set(xlabel="NCycles",ylabel='Chi-Square')
        ax1.grid(True)
        ax2.grid(True)
        fig1.canvas.draw()

    def draw_ini(self,Xexp,Yexp):
        plt.ion()
        fig, (ax) = plt.subplots(1, 1)
        ax.scatter(Xexp, Yexp, label='Experimental')
        line1, = ax.plot(Xexp, Yexp, label='Fitted', color='r')
        ax.set(xlabel="X", ylabel='Y')
        ax.grid(True)
        plt.legend(loc='best', shadow=False, fontsize='x-large')
        return fig, line1

    def draw(self,fig,line1):
        """ This routine updates the graph while the fitting is performed """
        def draw(YFit):
            line1.set_ydata(YFit)
            fig.canvas.draw()
        return draw

    def gsa(self,Xexp,Yexp,nDimension,func,X_0,lock,anim,step_anim,conv,crit_conv,NStopMax,factor):
        """ This routine initializes the gsa loop """

        #qA, qT, qV, To = np.array(qA,dtype='float64'),np.array(qT,dtype='float64'), np.array(qV,dtype='float64'), np.array(To,dtype='float64')
        D, qA1, qT1, qV1, Tqt, coef, exp1, exp2 = self.GSAini()

        X_0 = np.array(X_0)
        X_t = np.array(X_0)
        X_ini = np.array(X_0)
        self.X_Min = np.copy(X_0)
        func_0, YFit = func(X_0)
        func_t, self.YFit = func(X_0)
        self.func_Min = func_0

        Temperature = self.Temperature(Tqt,qT1)                     #Definindo a função da temperatura
        Delta_X = self.Delta_X(D, coef, qV1, exp1, exp2)            #Definindo a função Delta_X
        VarLock = self.VarLock(lock,X_ini)                          #Definindo a função VarLock

        self.func_conv['x'].append(0)
        self.func_conv['y'].append(func_0)
        self.func_conv_min['x'].append(0)
        self.func_conv_min['y'].append(func_0)


        if anim == True:
            fig, line1 = self.draw_ini(Xexp,Yexp)
            draw = self.draw(fig, line1)
        for t in range(1,NStopMax+1):
            T = Temperature(t)
            dx = np.array([Delta_X(T) for x in range(nDimension)])
            #print(dx.shape)
            #print(factor.shape)
            X_t = X_0 + dx * factor

            X_t = VarLock(X_t)
            func_t, YFit = func(X_t)
            if func_t <= func_0:
                X_0 = X_t.copy()
                func_0 = func_t
                self.func_conv['x'].append(t)
                self.func_conv['y'].append(func_t)
                if func_t <= self.func_Min:
                    self.func_Min = func_t
                    self.YFit = YFit
                    self.X_Min = X_t.copy()
                    self.func_conv_min['x'].append(t)
                    self.func_conv_min['y'].append(func_t)
                    if anim and len(self.func_conv_min) % step_anim == 0:
                        draw(self.YFit)
                    if conv and self.func_Min < crit_conv:
                        self.plot_convergence(t)
                        return self.func_Min, self.X_Min, self.func_conv , self.func_conv_min
            elif self.qA != 1.0:
                DeltaE = func_t - func_0
                PqA =  1.0 / (( 1.0 + qA1 * DeltaE / T) ** (1.0 / qA1))
                if random.random() < PqA:
                    X_0 = X_t.copy()
                    func_0 = func_t
        if anim == True:
            draw(self.YFit)
        self.plot_convergence(NStopMax)
        return self.func_Min, self.X_Min, self.func_conv , self.func_conv_min

if __name__ == '__main__':
    x = np.array([-5.0, -4.0, -3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0, 4.0])
    y = np.array([66.0, 45.0, 28.0, 15.0, 6.0, 1.0, 0.0, 3.0, 10.0, 21.0])
    def func(a):
        YFit = a[0] * x * x + a[1] * x + a[2]
        erro = YFit - y
        return sum(erro * erro) / len(y), YFit
    X_0 =  np.array([0.1, 0.1, 0.1])
    #X_0 = np.array([ 2.08007311, -2.9792965,   1.04705355])
    a = gsa_py(1.5,1.1, 1.1, 1.1)
####a.gsa(X, Y, nD, func, X_0, var_lock, animVar, step_anim, convVar, conv_crit, NStopMax, qA,qT, qV, To)
    a.gsa(x, y, 3, func, X_0, [False, False, False], True, 10, False, 0.1, 1000)

    print(a.X_Min)
    print(a.func_Min)


    t = tk.Tk()
    t.mainloop()



