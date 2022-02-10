from kivy.properties import ObjectProperty
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.screenmanager import Screen
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
import matplotlib.pyplot as plt
import med_tubo
import plots_tubo
import os
import h5py
import pytta


class TuboWindow(Screen):
    pass


class SigMonTubo(Screen):
    box_lvl = ObjectProperty(None)
    label_in = []
    label_out = []
    conta = 0
    direta = []
    inversa = []
    def __init__(self, **kwargs):
        super(SigMonTubo, self).__init__(**kwargs)


    def med_tubo(self):
        path = self.manager.get_screen('tubo_imp').ids

        ls2 = [path.med_name.text, path.sinal.text, path.sample_rate.text, path.fft_degree.text, path.out_amp.text,
               path.tub_diam.text, path.temp.text, path.dist_mic.text, path.dist_amst.text,
               path.L_amst.text, path.gap_amst.text]

        # global measure, f, TF, f_coere, coere, flag, max_lvl_in, max_lvl_out

        [self.measure, self.f, self.TF, self.f_coere, self.coere,
         self.flag, self.max_lvl_in, self.max_lvl_out] = med_tubo.tubo_imp(*ls2)

        return self.measure, self.f, self.TF, self.f_coere, self.coere, self.flag, self.max_lvl_in, self.max_lvl_out

    def on_enter(self, *args):
        print('conta_monitor', SigMonTubo.conta)
        SigMonTubo.conta = SigMonTubo.conta + 1

        if SigMonTubo.conta == 1:

            self.direta = SigMonTubo.med_tubo(self)
            if self.direta[5] == True:
                SigMonTubo.set_levels(self, self.direta[6], self.direta[7])

        if SigMonTubo.conta == 2:

            self.inversa = SigMonTubo.med_tubo(self)
            if self.inversa[5] == True:
                SigMonTubo.set_levels(self, self.inversa[6], self.inversa[7])
                SigMonTubo.med_tubo_H(self)

    def med_tubo_H(self):
        sig_mon = self.manager.ids.sig_mon_tubo
        self.H_12, self.H_c, self.alpha, self.f_alpha = med_tubo.transfer_function(sig_mon.direta[2], sig_mon.inversa[2])

        return self.H_12, self.H_c, self.alpha, self.f_alpha

    def set_levels(self, max_lvl_in, max_lvl_out):
        anim_lvl_in = []
        for n in range(len(self.max_lvl_in)):
            anim_lvl_in.append(int(300 + 5 * self.max_lvl_in[n]))

            SigMonTubo.label_in.append(LabelIn(anim_height=anim_lvl_in[n]))
            self.manager.get_screen('sig_mon_tubo').ids.box_in.add_widget(SigMonTubo.label_in[n])

        anim_lvl_out = int(300 + 5 * self.max_lvl_out)

        SigMonTubo.label_out.append(LabelIn(anim_height=anim_lvl_out))
        # SigMonitor.animate(self, SigMonSala.label_out[0], anim_lvl_out)

        #Adiciona a barra de nível na tela
        self.manager.get_screen('sig_mon_tubo').ids.box_out.add_widget(SigMonTubo.label_out[0])

        # print(type(sala_analise))
        self.manager.get_screen('sig_mon_tubo').ids.box_out.children[0].text = (
                'Saída : \n ' + str(round(self.max_lvl_out)) + ' [dBFS]')

        self.manager.get_screen('sig_mon_tubo').ids.box_out.children[0].pos = self.width * .2, self.height * .01

        # Altera a cor das barras conforme o valor dBFS
        if self.max_lvl_out > 0:
            SigMonTubo.label_out[0].rect_color.rgba = (1, 0, 0, 1)

        elif self.max_lvl_out > -5:
            SigMonTubo.label_out[0].rect_color.rgba = (1, .4, .0, 1)

        elif -5 >= self.max_lvl_out >= -20:
            SigMonTubo.label_out[0].rect_color.rgba = (0, 1, 0, 1)

        else:
            SigMonTubo.label_out[0].rect_color.rgba = (.6, .4, .2, 1)

        # SigMonTubo.animate(self, self.ids.box_out.children[0], anim_lvl_out)

        for j in range(len(self.max_lvl_in)):
            self.manager.get_screen('sig_mon_tubo').ids.box_in.children[j].text = (
                    'Entrada Canal ' + str(j + 1) + ' : \n ' + '  ' + str(round(max_lvl_in[j])) + ' [dBFS]')

            self.manager.get_screen('sig_mon_tubo').ids.box_in.children[j].pos = self.width * .3 * (
                        1 + j), self.height * .01

            # SigMonitor.animate(self, self.ids.box_bar.children[j], anim_lvl_in[j])

            # Altera as cores das barras conforme o valor dBFS

            if self.max_lvl_in[j] > 0:
                SigMonTubo.label_in[j].rect_color.rgba = (1, 0, 0, 1)
                self.manager.get_screen('sig_mon_tubo').ids.box_in.children[j].text = (
                        'Entrada Canal ' + str(j + 1) + ' : \n ' + '  ' + str(round(max_lvl_in[j])) + ' [dBFS] \n'
                        + 'OCORREU CLIPPING!!!')

            elif self.max_lvl_in[j] > -5:
                SigMonTubo.label_in[j].rect_color.rgba = (1, .4, .0, 1)

            elif -5 >= self.max_lvl_in[j] >= -20:
                SigMonTubo.label_in[j].rect_color.rgba = (0, 1, 0, 1)

            else:
                SigMonTubo.label_in[j].rect_color.rgba = (.6, .4, .2, 1)

    def segue(self):
        if SigMonTubo.conta == 1:
            self.manager.current = 'plot_wdw2'

        if SigMonTubo.conta == 2:
            self.manager.current = 'plot_wdw'
            sig_mon = self.manager.ids.sig_mon_tubo.zera_cont()

    def volta(self):
        if SigMonTubo.conta == 1:
            self.manager.current = 'tubo_imp'
            SigMonTubo.conta = 0

        if SigMonTubo.conta == 2:
            self.manager.current = 'invert'
            #print('sigmon_cont', SigMonTubo.conta)
            SigMonTubo.conta = 1

    def remove(self):
        self.manager.get_screen('sig_mon_tubo').ids.box_out.remove_widget(SigMonTubo.label_out[0])

        for n in range(2):
            self.manager.get_screen('sig_mon_tubo').ids.box_in.remove_widget(SigMonTubo.label_in[n])


class LabelIn(Label):
    def __init__(self, anim_height, **kwargs):
        super(LabelIn, self).__init__(**kwargs)
        self.anim_height = anim_height

        with self.canvas.before:
            Color(.5, .8, .6, mode='rgb')
            self.rectf = Rectangle(pos=(self.width * 5, self.height * 7), size=(100, 80))

        with self.canvas:
            self.rect_color = Color(rgba=(.49, .12, .7, 1))
            self.rect = Rectangle(pos=self.pos, size=(40, 0))

        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)

    def update_rect(self, *args):
        self.rectf.pos = self.center_x - 100, self.center_y - 30
        self.rectf.size = 190, 65
        self.rect.pos = (self.center_x - 20), self.height * .65
        self.rect.size = (40, self.anim_height)


class PlotWindow(Screen):
    box = ObjectProperty(None)
    conta = 0

    def add_plot(self, dx, dy, title):
        fig1 = plt.figure()
        axes = fig1.subplots()
        axes.plot(dx, dy)
        axes.set_title(title)
        axes.set_xlabel('Frequência [Hz]')
        # axes.set_ylabel('Coerência')
        # self.fig2 = m_frf.plot_freq(decimalSep='.')

        self.fig1 = plt.gcf()
        return self.fig1

    def forward(self, conta):
        sig_mon = self.manager.ids.sig_mon_tubo
        PlotWindow.conta = int(conta) + 1
        print(PlotWindow.conta)
        if PlotWindow.conta == 1:
            self.fig1 = PlotWindow.add_plot(self, sig_mon.f, sig_mon.H_12, 'Função de transferência entre as duas configurações')
            self.box.add_widget(FigureCanvasKivyAgg(self.fig1))
        if PlotWindow.conta == 2:
            self.fig1 = PlotWindow.add_plot(self, sig_mon.f, sig_mon.H_c, 'Calibração')
            self.box.add_widget(FigureCanvasKivyAgg(self.fig1))
        elif PlotWindow.conta == 3:
            self.fig1 = PlotWindow.add_plot(self, sig_mon.f_alpha, sig_mon.alpha, 'Coeficiente de absorção')
            self.box.add_widget(FigureCanvasKivyAgg(self.fig1))
        elif PlotWindow.conta == 4:
            self.manager.current = 'primeira'
            PlotWindow.save(self)
            PlotWindow.conta = 0

        print(PlotWindow.conta)

    def backward(self, conta):
        PlotWindow.conta = int(conta) - 1

        sig_mon = self.manager.ids.sig_mon_tubo

        if PlotWindow.conta == -1:
            self.manager.current = 'tubo_imp'
            PlotWindow.conta = 0

        elif PlotWindow.conta == 0:
            self.fig1 = PlotWindowConf.add_plot2(self, sig_mon.inversa[1], sig_mon.inversa[2],
                                                 sig_mon.inversa[4], 'Função de transferência - 2ª configuração')
            self.box.add_widget(FigureCanvasKivyAgg(self.fig1))
            print(PlotWindow.conta)

        elif PlotWindow.conta == 1:
            self.fig1 = PlotWindow.add_plot(self, sig_mon.f, sig_mon.H_12, 'Função de transferência entre as duas configurações')
            self.box.add_widget(FigureCanvasKivyAgg(self.fig1))
            print(PlotWindow.conta)

        elif PlotWindow.conta == 2:
            self.fig1 = PlotWindow.add_plot(self, sig_mon.f, sig_mon.H_c, 'Calibração')
            self.box.add_widget(FigureCanvasKivyAgg(self.fig1))

        elif PlotWindow.conta == 3:
            self.fig1 = PlotWindow.add_plot(self, sig_mon.f_alpha, sig_mon.alpha, 'Coeficiente de absorção')
            self.box.add_widget(FigureCanvasKivyAgg(self.fig1))

        print(PlotWindow.conta)

    def on_enter(self, *args):
        sig_mon = self.manager.ids.sig_mon_tubo
        self.fig1 = PlotWindowConf.add_plot2(self, sig_mon.inversa[1], sig_mon.inversa[2], sig_mon.inversa[4],
                                             'Função de transferência - 2ª configuração')
        self.box.add_widget(FigureCanvasKivyAgg(self.fig1))

    def clear(self):
        self.box.clear_widgets()
        self.box.remove_widget(FigureCanvasKivyAgg(self.fig1))
        plt.cla()
        plt.close('all')

    def save(self):
        sig_mon = self.manager.ids.sig_mon_tubo

        #dir = (r'C:\Users\Joaodavi\Documents\Estágio\SAGUI\Tubo_Impedância_')
        dir = ('~/Desktop/Resultados/Resultados_')

        med_name = self.manager.get_screen('tubo_imp').ids.med_name.text
        if os.path.isdir(dir + med_name):
            pass
        else:
            os.mkdir(dir + med_name)



        # Salva a medição em um arquivo .h5
        hf = h5py.File(dir + med_name + '\\tubo_impedancia_' + med_name + '.h5', 'w')
        g1 = hf.create_group('Dados')

        g1.create_dataset('Direta_freq', data=sig_mon.direta[1])
        g1.create_dataset('Direta_TF', data=sig_mon.direta[2])
        g1.create_dataset('Direta_freq_coere', data=sig_mon.direta[3])
        g1.create_dataset('Direta_coere', data=sig_mon.direta[4])

        g1.create_dataset('Inversa_freq', data=sig_mon.inversa[1])
        g1.create_dataset('Inversa_TF', data=sig_mon.inversa[2])
        g1.create_dataset('Inversa_freq_coere', data=sig_mon.inversa[3])
        g1.create_dataset('Inversa_coere', data=sig_mon.inversa[4])

        g1.create_dataset('Função Transferência', data=sig_mon.H_12)
        g1.create_dataset('Calibração', data=sig_mon.H_c)
        g1.create_dataset('Freq', data=sig_mon.f)
        g1.create_dataset('Freq_Abs', data=sig_mon.f_alpha)
        g1.create_dataset('Coef_Abs', data=sig_mon.alpha)

        plots_tubo.save((dir + med_name), ('\\tubo_impedancia_' + med_name + '.h5'))

        pytta.save((dir + med_name + '\\tubo_direta_' + med_name + '.hdf5'), sig_mon.direta[0])
        pytta.save((dir + med_name + '\\tubo_inversa_' + med_name + '.hdf5'), sig_mon.inversa[0])

class PlotWindowConf(Screen):
    box2 = ObjectProperty(None)

    # conta = 0

    def add_plot2(self, f, TF, coere, title):
        sig_mon = self.manager.ids.sig_mon_tubo

        fig2 = plt.figure()
        H12 = fig2.add_subplot(211)
        H12.plot(f, TF)
        H12.set_xlim([20, 1000])
        H12.set_title(title)
        H12.set_ylabel("Magnitude [dB]")
        H12 = fig2.add_subplot(212)
        H12.plot(sig_mon.f_coere, coere)
        H12.set_xlim([20, 1000])
        H12.set_ylabel('Coerência')
        self.fig2 = plt.gcf()

        return self.fig2

    def on_enter(self, *args):
        sig_mon = self.manager.ids.sig_mon_tubo
        PlotWindowConf.add_plot2(self, sig_mon.direta[1], sig_mon.direta[2], sig_mon.direta[4],
                                 "Função de transferência - 1ª configuração")
        self.box2.add_widget(FigureCanvasKivyAgg(self.fig2))

    def clear(self):
        self.box2.remove_widget(FigureCanvasKivyAgg(self.fig2))
        plt.cla()
        self.box2.clear_widgets()
        # self.fig2 = PlotWindow.add_plot(self, 1000)
        # self.box2.add_widget(FigureCanvasKivyAgg(self.fig2))


class Inverte(Screen):
    pass
