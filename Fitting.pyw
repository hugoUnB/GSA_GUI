from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
import sys
import numpy as np
import GSA as gsa
import time
import os

class Fitting(Tk):
    __author__ = "Kleber C. Mundim, Hugo G. Machado"
    __version__ = "1.0.1"
    __license__ = "GPL"
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        self.geometry("850x670+50+50")
        self.title('GSA Fitting')
        self.resizable(False, False)
        Label(self, text="GSA Fitting", font=('arial', 30, 'bold')).pack(pady=15)

        ### Menu
        menu = Menu(self)
        self.config(menu=menu)
        subMenu = Menu(menu)
        menu.add_cascade(label='Help', menu=subMenu)
        subMenu.add_command(label='Help', command = self.Help)
        subMenu.add_command(label='Manual', command=self.Manual)
        subMenu.add_command(label='About', command = self.About)
        subMenu.add_separator()
        subMenu.add_command(label='Exit', command = self.Exit)

        ### dicts (entrada de dados, variáveis, labels e checkbuttons)
        self.ed = {}
        self.Var = {}
        self.lb = {}
        self.cb = {}

        ### LEFT
        frame_left = Frame(self)
        frame_left.pack(side=LEFT, padx=30)

        frame_gsaPar = LabelFrame(frame_left, text='GSA Parameters', bd=5)
        frame_gsaPar.pack(side=TOP, pady=7, fill=X)
        self.CriarFrameGSAPar(frame_gsaPar)

        self.frame_ini = LabelFrame(frame_left, text='Initial Parameters', bd=5)
        self.frame_ini.pack(side=TOP, pady=7, fill=X)
        self.janela_rolavel = JanelaRolavel(self.frame_ini)
        self.janela_rolavel.pack(side=TOP, pady=7)
        self.CriarFrameInitial(self.janela_rolavel)

        ### RIGHT
        frame_right = Frame(self)
        frame_right.pack(side=LEFT, padx=30)

        Label(frame_right, text='Function').pack(fill=BOTH, expand=True, padx=3)
        self.ed_func = Entry(frame_right, width=30)
        self.ed_func.pack(fill=X, expand=True,  padx=3)

        frame_right_box = Frame(frame_right)
        frame_right_box.pack(side=TOP, pady=7, )
        self.CriarBoxScroll(frame_right_box)

        frame_bt = Frame(frame_right)
        frame_bt.pack(side=TOP, pady=7)
        self.CriarButton(frame_bt)

    def CriarFrameGSAPar(self,parent):
        frames = {}
        for ind, txt, value in [
                ('qA', 'Acceptance index', '1.1'),
                ('qT', 'Temperature index', '1.5'),
                ('qV', 'Visiting index', '1.1'),
                ('To', 'Initial Temperature', '1.0E-00'),
                ('NStopMax', 'Max number of GSA-loops', '10000'),
                ('ND', 'nDimension', '5') ,
                ('Factor', 'Factor',1)]:
            frames[ind] = Frame(parent)
            frames[ind].pack(padx= 15, pady=5, anchor=W)
            self.ed[ind] = Entry(frames[ind])
            self.ed[ind].pack(side=LEFT)
            self.ed[ind].insert(1, value)
            if ind != 'ND':
                Label(frames[ind], text="({}) - {}".format(ind,txt)).pack(side=RIGHT)
            else:
                Button(frames[ind],text = "({}) - {}".format(ind,txt),command=self.ND).pack(side=RIGHT)

        for opt, txt1, txt2 in [('anim','Animation','Step Size'),
                                ('conv','Stop','Convergence Criterion')]:
            self.Var[opt] = BooleanVar()
            self.cb[opt] = Checkbutton(parent, text=txt1, variable=self.Var[opt], command= lambda opt=opt: self.change(opt))
            self.cb[opt].pack(anchor=W)
            frames[opt] = Frame(parent)
            frames[opt].pack(padx=15, pady=5, anchor=W)

            self.ed[opt] = Entry(frames[opt])
            self.ed[opt].pack(side=LEFT, padx=10)
            self.lb[opt] = Label(frames[opt], text=txt2)
            self.lb[opt].pack(side=LEFT)
            self.change(opt)

        #self.ed['anim'].pack_forget()
        #self.lb['anim'].pack_forget()

    def CriarFrameInitial(self,parent):
        self.filename = ''
        self.ChiSq = Label(parent.conteudo, text='Chi-square: ')
        self.ChiSq.pack()

        self.f_init_par = {}
        self.LockVar = {}
        for ind in range(int(self.ed['ND'].get())):
            self.f_init_par[ind] = Frame(parent.conteudo)
            self.f_init_par[ind].pack(pady=7, anchor=W, expand=True)
            Label(self.f_init_par[ind], text="a[{}]  ".format(ind),font=('arial','10')).pack(side=LEFT,padx=5)
            self.ed[ind] = Entry(self.f_init_par[ind],width=20)
            self.ed[ind].pack(side=LEFT, padx=35)
            self.ed[ind].insert(0, '0.1')
            self.LockVar[ind] = BooleanVar()
            self.cb[ind] = Checkbutton(self.f_init_par[ind], text='Lock', variable=self.LockVar[ind])
            self.cb[ind].pack(side=LEFT,padx=10)

    def CriarBoxScroll(self,parent):
        frame1 = Frame(parent) ; frame1.pack(side=LEFT)
        frame2 = Frame(parent) ; frame2.pack(side=LEFT)

        Label(frame1, text='X', font=('arial', 10)).pack()
        self.txt_l = Text(frame1, height=28, width=19)
        self.txt_l.pack(fill=BOTH, expand=True, padx=3)

        Label(frame2, text='Y', font=('arial', 10)).pack()
        self.txt_r = Text(frame2, height=28, width=20)
        self.txt_r.pack(fill=BOTH, expand=True, side=LEFT,padx=3)

        self.scrollbar = Scrollbar(frame2)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        # Changing the settings to make the scrolling work
        self.scrollbar['command'] = self.on_scrollbar
        self.txt_l['yscrollcommand'] = self.on_textscroll
        self.txt_r['yscrollcommand'] = self.on_textscroll

    def CriarButton(self,parent):
        for txt, cmd in [('Open file',self.Open),
                         ('Clear',self.Clear),
                         ('Fitting', self.Fit),
                         ('Save',self.Save)]:
            Button(parent, text=txt, command=cmd, font=('Arial', 10,'bold'), width=8,height=1).pack(side=LEFT,pady = 5, padx=7, anchor=CENTER)

    def Open(self):
        self.filename = filedialog.askopenfilename(title="Select file",filetypes=[(".txt files", "*.txt;*.dat"), ("all files", "*.*")])
        if not os.path.isfile(self.filename):
            return
        self.txt_l.delete(0.0, END)
        self.txt_r.delete(0.0, END)
        for delimiter in ['\t', ',', ';']:
            try:
                dados = np.loadtxt(self.filename, delimiter=delimiter)
            except:
                pass
        try:
            X, Y = dados[:, 0], dados[:, 1]
        except:
            messagebox.showerror(title='Error', message='Select file in csv format')

        for i in range(len(X)):
            self.txt_l.insert(float(i + 1), str(X[i]) + '\n')
            self.txt_r.insert(float(i + 1), str(Y[i]) + '\n')

    def Clear(self):
        for ind in range(len(self.f_init_par)):
            self.ed[ind].delete(0, END)
            self.ed[ind].insert(0, '0.1')
            self.cb[ind].deselect()
        for opt in ['anim','conv']:
            self.cb[opt].deselect()
            self.change(opt)

    def Save(self):
        try:
            filename = filedialog.asksaveasfilename(title="Save File", defaultextension='txt', filetypes=(
                ("txt files", "*.txt"), ("dat files", "*.dat"), ("all files", "*.*")))
            out = open(filename, 'w', encoding="utf-8")
            for n in range(len(self.a.X_Min)):
                out.writelines('a[{}] = {}\n'.format(n, self.a.X_Min[n]))
            out.writelines('\n{:^20s} {:^20s} {:^20s} \n'.format('Xexp', 'Yexp', 'Yfit'))
            for n in range(len(self.X)):
                Xn = '{:<.15f}'.format(self.X[n])
                Yn = '{:<.15f}'.format(self.Y[n])
                YFitn = '{:<.15f}'.format(self.a.YFit[n])
                out.writelines('{:<20s} {:<20s} {:<20s} \n'.format(Xn, Yn, YFitn))

            out.writelines('\n\nfunc: y(x) = {}\n'.format(self.func))
            out.writelines('\nChi-Square = {:.15f}\n'.format(self.a.func_Min))
            out.close()
        except:
            messagebox.showerror(title='Error', message='Perform the fitting before saving the file')

    def Fit(self):
        ### GSA parameters
        try:
            qA = float(self.ed['qA'].get())
            qT = float(self.ed['qT'].get())
            qV = float(self.ed['qV'].get())
            NStopMax = int(self.ed['NStopMax'].get())
            To = float(self.ed['To'].get())
            nDimension = int(self.ed['ND'].get())
            Factor = np.array(self.ed['Factor'].get().split(','),dtype=np.float64)
        except:
            messagebox.showerror(title='Error', message='Invalid GSA parameters')
            return
        print(Factor)
        print(type(Factor))
        print(Factor[0])
        """
        try:
            Factor = int(self.ed['Factor'].get())
            print('int')
        except:
            try:
                Factor = np.array(self.ed['Factor'].get())
                print('arrray')
            except:
                messagebox.showerror(title='Error', message='Invalid Factor')
                return
        """
        ### Initial Parameters
        try:
            X_0 = []
            for n in range(nDimension):
                X_0.append(float(self.ed[n].get()))
        except:
            messagebox.showerror(title='Error', message='Invalid Initial parameters')
            return

        ### X
        X = self.txt_l.get(0.0, END)
        X = X.split('\n')
        X_corr = [float(x) for x in X if len(x) > 0 and not x.isspace()]

        ### Y
        Y = self.txt_r.get(0.0, END)
        Y = Y.split('\n')
        Y_corr = [float(y) for y in Y if len(y) > 0 and not y.isspace()]

        if len(X_corr) != len(Y_corr):
            messagebox.showerror(title='Error', message='Difference in the number of points between X and Y ')
            return
        if len(X_corr) == 0 or len(Y_corr) == 0:
            messagebox.showerror(title='Error', message='Enter the values of X and Y ')
            return
        ### anim
        animVar = self.Var['anim'].get()
        if animVar:
            try:
                step_anim = int(self.ed['anim'].get())
            except:
                messagebox.showerror(title='Error', message='The step size of animation must be an integer')
                return
        else:
            step_anim = 1
        ### Stop (conv. crit.)
        convVar = self.Var['conv'].get()
        if convVar:
            try:
                conv_crit = float(self.ed['conv'].get())
            except:
                messagebox.showerror(title='Error', message='The Convergence Criterion must be a real number')
                return
        else:
            conv_crit = 1

        ### Lock
        var_lock = []
        for i in range(len(self.LockVar)):
            var_lock.append(self.LockVar[i].get())

        self.WriteFunc(X_corr, Y_corr)
        try:
            import func
        except:
            messagebox.showerror(title='Error', message='The function is incorrect')
            return

        #### Execute
        inicio = time.time()
        a = gsa.gsa_py(qA,qT,qV,To)
        a.gsa(X_corr, Y_corr, nDimension, func.func, X_0, var_lock, animVar, step_anim, convVar, conv_crit, NStopMax,Factor)
        print('Tempo gasto no ajuste: ', time.time() - inicio, 'seg')

        del func
        del sys.modules['func']

        self.a = a
        self.X, self.Y = X_corr, Y_corr
        print('Parametros ajustados: ', a.X_Min)
        print('Chi-quadrado: ', a.func_Min)
        self.write_parameters(a, nDimension)

    def write_parameters(self, a, ND):
        for n in range(ND):
            self.ed[n].delete(0, END)
            self.ed[n].insert(1, str(a.X_Min[n]))

        self.ChiSq['text'] = ' Chi-square: ' + str(a.func_Min)

    def ND(self):
        try:
            int(self.ed['ND'].get())
        except:
            messagebox.showerror(title='Error',message='The nDimension value must be an integer')
            return
        self.janela_rolavel.destroy()
        self.janela_rolavel = JanelaRolavel(self.frame_ini)
        self.janela_rolavel.pack(side=TOP, pady=7)
        self.CriarFrameInitial(self.janela_rolavel)

    def change(self,opt):
        if self.Var[opt].get():
            value = 1
        else:
            value = 0
        state, bg, fg = [(DISABLED, 'gray95', 'gray'), (NORMAL, 'white', 'black')][value]

        self.ed[opt].delete(0, END)
        self.ed[opt]['state'] = state
        self.ed[opt]['bg'] = bg
        self.lb[opt]['fg'] = fg

        if opt == 'anim':
            #self.ed[opt].insert(0, str(int(int(self.ed['NStopMax'].get())) / 100).split('.')[0])
            self.ed[opt].insert(0, '1')
        elif opt == 'conv':
            self.ed[opt].insert(0,'0.01')

    def WriteFunc(self, X_corr, Y_corr):
        self.func = self.ed_func.get()
        file_func = open('func.py', 'w')
        head = ['import numpy  as np\n',
                'x= np.array(' + str(X_corr) + ') \n',
                'yexp= np.array(' + str(Y_corr) + ') \n',
                'def func(a):\n', ]
        tail = ['\terro = y - yexp\n',
                '\treturn np.array(sum(erro * erro) / len(yexp)), y\n']
        file_func.writelines(head)

        if '=' not in self.func:
            file_func.writelines('\ty = {}\n'.format(self.func.lower()))
        else:
            file_func.writelines('\t{}\n'.format(self.func.lower()))
        file_func.writelines(tail)
        file_func.close()

    def on_scrollbar(self, *args):
        self.txt_l.yview(*args)
        self.txt_r.yview(*args)

    def on_textscroll(self, *args):
        self.scrollbar.set(*args)
        self.on_scrollbar('moveto', args[0])

    def Help(self):
        t = Toplevel(self)
        t.geometry("750x500")
        t.resizable(False,False)
        jr = JanelaRolavel(t)
        jr.pack(side=TOP, pady=25)
        Label(jr.conteudo, text='\nBRIEF TUTORIAL',font=('Arial','12','bold')).pack()

        Label(jr.conteudo, text='\tThe GSA methods is used to fit functions in experimental data. It is based on the', font=('Arial', '10')).pack(anchor=W,padx=5)
        Label(jr.conteudo, text='\tcorrelation between the minimization of a cost function (or objective) obtained through a', font=('Arial', '10')).pack(anchor=W,padx=5)
        Label(jr.conteudo, text='\tslow cooling. In this method, an artificial temperature is introduced and gradually cooled', font=('Arial', '10')).pack(anchor=W,padx=5)
        Label(jr.conteudo, text='\tin complete analogy with the well known annealing technique, frequently used in', font=('Arial', '10')).pack(anchor=W,padx=5)
        Label(jr.conteudo, text='\tmetallurgy when a molten metal reaches its crystalline state (global minimum of the', font=('Arial', '10')).pack(anchor=W,padx=5)
        Label(jr.conteudo, text='\tthermodynamics energy). In our case the temperature is intended as an external noise.', font=('Arial', '10')).pack(anchor=W,padx=5)

        Label(jr.conteudo, text='\n\tGSA REQUIRED PARAMETERS:', font=('Arial', '12', 'bold')).pack(anchor=W,padx=5)
        Label(jr.conteudo, text='\t\tqA : Acceptance index ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tqT: Temperature index ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tqV  : Visiting index ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tTo  : Initial Temperature',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tNStopMax is number of parameters used in the function to be optimized. ',font=('Arial', '10')).pack(anchor=W)

        Label(jr.conteudo, text='\t*Obs.',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\tThe q’s parameters are positive real numbers different of 1, except the qA. The ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\tprogram, initially, present some default parameters.',font=('Arial', '10')).pack(anchor=W)

        Label(jr.conteudo, text='\n\t"To parameter": In this procedure, the artificial temperature (To) is introduced and ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\tgradually cooled, in complete analogy with the well known annealing technique ', font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\tfrequently used in metallurgy when a molten metal reaches its crystalline state (global ', font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\tminimum of the thermodynamical energy). In this case the temperature is intended as ', font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\tan external noise. See the basic references.', font=('Arial', '10')).pack(anchor=W)

        Label(jr.conteudo, text='\n\tFUNCTION:', font=('Arial', '12', 'bold')).pack(anchor=W,padx=5)
        Label(jr.conteudo, text='\t\tHow to enter the objective function, or cost function, used in the fitting  ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tprocedure? There are 2 options:',font=('Arial', '10')).pack(anchor=W)

        Label(jr.conteudo, text='\n\t\t1)- Using the functions included in NumPy scientific package for Python. ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tExamples: np.sin(x),  np.exp(x) and others. In this case the ‘np.’ is mandatory. ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tFor additional informations see: ', font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\thttps://www.numpy.org/devdocs/user/quickstart.html', font=('Arial', '10')).pack(anchor=W)

        Label(jr.conteudo, text='\n\t\t2) Create a user-defined fitting function through the Fitting Function Box. The ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tformatted text fields provide a way for user to introduce the own function as for ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\texample: a[0]*x**2 + a[1]*x + a[2]  for a quadratic function type.', font=('Arial', '10')).pack(anchor=W)


        Label(jr.conteudo, text='\n\tFUNCTION INITIAL CONSTANTS:', font=('Arial', '12', 'bold')).pack(anchor=W,padx=5)
        Label(jr.conteudo, text='\t\ta[i] are the constants used in the function definition as for example the quadratic ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tfunction f = a[0]*x**2 + a[1]*x + a[2]. x is the independent variable.',font=('Arial', '10')).pack(anchor=W)

        Label(jr.conteudo, text='\n\t\tLock: Check box to lock a parameter. In this case, it is not changed during the ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tadjustment procedure.',font=('Arial', '10')).pack(anchor=W)

        Label(jr.conteudo, text='\n\tGRAPHICS OPTIONS:', font=('Arial', '12', 'bold')).pack(anchor=W,padx=5)
        Label(jr.conteudo, text='\t\tAnimation: The ‘Check Boxes’ must be activated to show function fitting procedure.',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\n\t\tStep Size field: refers to the number of steps in order to update graphic animation. ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\n\t\t* Too low values in the ‘StepSize’ will cause the chart updates excessively,',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\twhich may leave the adjustment slow.',font=('Arial', '10')).pack(anchor=W)

        Label(jr.conteudo, text='\n\tBUTTONS:', font=('Arial', '12', 'bold')).pack(anchor=W,padx=5)
        Label(jr.conteudo, text='\t\tOpen File: Click in the button to upload the file with input data. The X,Y data ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tmust be separated by a single comma in the input file, like in ‘csv’ format.',font=('Arial', '10')).pack(anchor=W)

        Label(jr.conteudo, text='\n\t\tFitting: Click to start the fit procedure. The process completes when the ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tdifference between reduced chi-square values of two successive iterations is ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tless than a certain tolerance value or when the maximum number of cycles ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\t(NStopMax) is reached.  When the process completes, we say that the fit has ',font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tconverged.',font=('Arial', '10')).pack(anchor=W)

        Label(jr.conteudo, text='\n\t\tSave: Click to save final results and additional informations. The Save Dialog ', font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tcan be used to write output file name and to select local to save it.', font=('Arial', '10')).pack(anchor=W)

        Label(jr.conteudo, text='\n\tREFERENCE:', font=('Arial', '12', 'bold')).pack(anchor=W, padx=5)
        Label(jr.conteudo, text='\t\tBasic reference: Mundim, K. C. and Tsallis, C. Int. J. Quantum Chem. (1996) 58, 373.\t\t', font=('Arial', '10')).pack(anchor=W)
        Label(jr.conteudo, text='\t\tFor additional information access: www.cursosvirtuais.pro.br/GSA/', font=('Arial', '10')).pack(anchor=W)

    def Manual(self):
        try:
            os.startfile("Help.pdf")
        except:
            messagebox.showerror(title='Error',message='Please Download the manual at the address: XXXX')
    def About(self):
        t = Toplevel(self)
        t.geometry("600x120")
        t.resizable(False, False)
        Label(t, text="\nPrograma desenvolvido por Kleber C. Mundim e Hugo G. Machado. Versão 1.0.1.\n\n\n Para relatar bugs ou tirar dúvidas mande um e-mail para:\n\n hugogontijomachado@gmail.com").pack()

    def Exit(self):
        self.destroy()

class JanelaRolavel(Frame):
    def __init__(self, parent, *args, **kw):
        Frame.__init__(self, parent, *args, **kw)

        # cria um canvas e uma barra de rolagem para rolá-lo:
        rolagem = Scrollbar(self, orient=VERTICAL)
        rolagem.pack(fill=Y, side=RIGHT, expand=FALSE)
        self.canvas = Canvas(self, bd=0, highlightthickness=0,
                        yscrollcommand=rolagem.set)
        self.canvas.pack(side=LEFT, fill=BOTH, expand=TRUE)
        rolagem.config(command=self.canvas.yview)

        # reseta a visão:
        self.canvas.xview_moveto(0)
        self.canvas.yview_moveto(0)

        # cria um frame dentro do canvas
        # para que seja rolado junto com ele:
        self.conteudo =  Frame(self.canvas)
        self.id_conteudo = self.canvas.create_window(
            0, 0, window=self.conteudo, anchor=NW)

        # cria eventos para detectar mudanças no canvas
        # e sincronizar com a barra de rolagem:
        self.conteudo.bind('<Configure>', self._configurar_conteudo)
        self.canvas.bind('<Configure>', self._configurar_canvas)

    def _configurar_conteudo(self, evento):
            # atualiza a barra de rolagem para o tamanho do frame de conteudo:
            tamanho = (
                self.conteudo.winfo_reqwidth(),
                self.conteudo.winfo_reqheight()
            )
            self.canvas.config(scrollregion="0 0 %s %s" % tamanho)
            if self.conteudo.winfo_reqwidth() != self.canvas.winfo_width():
                # atualizar tambem a largura do canvas para caber o conteudo:
                self.canvas.config(width=self.conteudo.winfo_reqwidth())

    def _configurar_canvas(self, evento):
        if self.conteudo.winfo_reqwidth() != self.canvas.winfo_width():
            # atualizar tambem a largura do conteudo para preencher o canvas:
            self.canvas.itemconfigure(
                self.id_conteudo, width=self.canvas.winfo_width())

if __name__ == "__main__":
    root = Fitting()
    root.mainloop()