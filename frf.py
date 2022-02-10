from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
import med_frf
import matplotlib.pyplot as plt
#import numpy as np
#import csv
import os
import h5py

import plots_frf


class FRFWindow(Screen):
    pass

class SigMonFRF(Screen):
    label_in = []
    label_out = []
    def medicao_frf(self):
        path = self.manager.get_screen('frf_wdw').ids

        lst_frf = [path.med_name.text, path.sinal.text, path.f_min.text, path.f_max.text, path.sample_rate.text,
                    path.fft_degree.text, path.out_amp.text, path.num_ch_in.text, path.num_ch_out.text, path.temp.text]

        self.FRF, self.m_frf, self.f_coere, self.coere, self.flagFRF, self.max_lvl_in, self.max_lvl_out = med_frf.frf(*lst_frf)

        return self.FRF, self.m_frf, self.f_coere, self.coere, self.flagFRF, self.max_lvl_in, self.max_lvl_out


    def on_enter(self, *args):
        SigMonFRF.medicao_frf(self)

        if self.flagFRF == True:
            SigMonFRF.set_levels(self)
            #self.manager.current = 'plot_wdw_frf'

    def set_levels(self):
        anim_lvl_in = []

        for n in range(len(self.max_lvl_in)):
            anim_lvl_in.append(int(300 + 5 * self.max_lvl_in[n]))

            SigMonFRF.label_in.append(LabelIn(anim_height=anim_lvl_in[n]))
            self.manager.get_screen('sig_mon_frf').ids.box_bar.add_widget(SigMonFRF.label_in[n])

        anim_lvl_out = int(300 + 5 * self.max_lvl_out)
        SigMonFRF.label_out.append(LabelIn(anim_height=anim_lvl_out))
        #SigMonSala.animate(self, SigMonSala.label_out[0], anim_lvl_out)

        self.manager.get_screen('sig_mon_frf').ids.box_out.add_widget(SigMonFRF.label_out[0])


        #print(type(sala_analise))
        self.manager.get_screen('sig_mon_frf').ids.box_out.children[0].text = (
                'Saída Canal 1: \n ' + str(round(self.max_lvl_out)) + ' [dBFS]')

        self.manager.get_screen('sig_mon_frf').ids.box_out.children[0].pos = self.width*.2, self.height*.01

        #Altera a cor das barras conforme o valor dBFS
        if self.max_lvl_out > 0:
            SigMonFRF.label_out[0].rect_color.rgba = (1, 0, 0, 1)

        elif self.max_lvl_out > -5:
            SigMonFRF.label_out[0].rect_color.rgba = (1, .4, .0, 1)

        elif -5 >= self.max_lvl_out >= -20:
            SigMonFRF.label_out[0].rect_color.rgba = (0, 1, 0, 1)

        else:
            SigMonFRF.label_out[0].rect_color.rgba = (.6, .4, .2, 1)

        #SigMonFRF.animate(self, self.ids.box_out.children[0], anim_lvl_out)

        for j in range(len(self.max_lvl_in)):
            self.manager.get_screen('sig_mon_frf').ids.box_bar.children[j].text = (
                    'Entrada Canal ' + str(j+1) + ' : \n ' + '  ' + str(round(self.max_lvl_in[j])) + ' [dBFS]')

            self.manager.get_screen('sig_mon_frf').ids.box_bar.children[j].pos = self.width*.3*(1+j), self.height*.01

            #SigMonSala.animate(self, self.ids.box_bar.children[j], anim_lvl_in[j])

            #Altera as cores das barras conforme o valor dBFS

            if self.max_lvl_in[j] > 0:
                SigMonFRF.label_in[j].rect_color.rgba = (1, 0, 0, 1)
                self.manager.get_screen('sig_mon_frf').ids.box_in.children[j].text = (
                        'Entrada Canal ' + str(j + 1) + ' : \n ' + '  ' + str(round(self.max_lvl_in[j])) + ' [dBFS] \n'
                        + 'OCORREU CLIPPING!!!')

            elif self.max_lvl_in[j] > -5:
                SigMonFRF.label_in[j].rect_color.rgba = (1, .4, .0, 1)

            elif -5 >= self.max_lvl_in[j] >= -20:
                SigMonFRF.label_in[j].rect_color.rgba = (0, 1, 0, 1)

            else:
                SigMonFRF.label_in[j].rect_color.rgba = (.6, .4, .2, 1)

    def remove(self):
        self.manager.get_screen('sig_mon_frf').ids.box_out.remove_widget(self.label_out[0])

        for n in range(int(self.manager.get_screen('frf_wdw').ids.num_ch_in.text)):
            self.manager.get_screen('sig_mon_frf').ids.box_bar.remove_widget(self.label_in[n])


class LabelIn(Label):
    def __init__(self, anim_height, **kwargs):
        super(LabelIn, self).__init__(**kwargs)
        self.anim_height = anim_height


        with self.canvas.before:
            Color(.5, .8, .6, mode='rgb')
            self.rectf = Rectangle(pos=(self.width*5, self.height*7), size=(100, 80))

        with self.canvas:
            self.rect_color = Color(rgba=(0.49, 0.40, 0.10, 1))
            self.rect = Rectangle(pos=self.pos, size=(40, 0), group='ret')


        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)

    def update_rect(self, *args):
        self.rectf.pos = self.center_x-100, self.center_y-30
        self.rectf.size = 190, 65
        self.rect.pos = (self.center_x - 20), self.height*.65
        self.rect.size = (40, self.anim_height)


class PlotWindowFRF(Screen):
    box = ObjectProperty()
    conta = 0
    val_plot = []


    def add_plot(self, dx, dy, title):
        fig1 = plt.figure()
        axes = fig1.subplots()
        axes.semilogx(dx, dy)
        axes.set_title(title)
        axes.set_xlabel('Frequência [Hz]')
        #axes.set_ylabel('Coerência')
        #self.fig2 = m_frf.plot_freq(decimalSep='.')

        self.fig1 = plt.gcf()
        return self.fig1

    def on_pre_enter(self, *args):
        sig_mon = self.manager.ids.sig_mon_frf
        #self.fig1 = PlotWindowFRF.add_plot(self, m_frf.freqVector, 20*np.log10(abs(m_frf.freqSignal)/(2*pow(10, -5))) - 134, 'Resposta no domínio da frequência')
        self.fig1 = PlotWindowFRF.add_plot(self, sig_mon.m_frf.freqVector, sig_mon.FRF, 'FRF')
        self.box.add_widget(FigureCanvasKivyAgg(self.fig1))


    def forward(self):
        PlotWindowFRF.conta = PlotWindowFRF.conta + 1
        sig_mon = self.manager.ids.sig_mon_frf
        if PlotWindowFRF.conta == 1:
            self.fig1 = PlotWindowFRF.add_plot(self, sig_mon.f_coere, sig_mon.coere[1], 'Coerência')
            self.box.add_widget(FigureCanvasKivyAgg(self.fig1))
        else:
            self.manager.current = 'primeira'
            PlotWindowFRF.conta = 0

    def backward(self):
        PlotWindowFRF.conta = PlotWindowFRF.conta - 1
        sig_mon = self.manager.ids.sig_mon_frf
        if PlotWindowFRF.conta == -1:
            self.manager.current = 'frf_wdw'
        elif PlotWindowFRF.conta == 0:
            self.fig1 = PlotWindowFRF.add_plot(self, sig_mon.m_frf.freqVector, sig_mon.FRF, 'FRF')
            self.box.add_widget(FigureCanvasKivyAgg(self.fig1))
        elif PlotWindowFRF.conta == 1:
            self.fig1 = PlotWindowFRF.add_plot(self, sig_mon.f_coere, sig_mon.coere, 'Coerência')
            self.box.add_widget(FigureCanvasKivyAgg(self.fig1))



    def clear(self):
        self.box.clear_widgets()
        self.box.remove_widget(FigureCanvasKivyAgg(self.fig1))
        plt.close('all')


    def save(self):
        sig_mon = self.manager.ids.sig_mon_frf
        #Organiza os valores para salvar os arquivos com os nomes correspondentes
        # figure_dict = {'Freq': 0, 'FRF': 1, 'Coerência': 2}
        # for name,  valor in figure_dict.items():
        #     if valor == PlotWindowFRF.conta:
        #         nome = name
        #dir = (r'C:\Users\Joaodavi\Documents\Estágio\FRF_')
        dir = ('~/Desktop/Resultados/Resultados_')
        med_name = str(self.manager.get_screen('frf_wdw').ids.med_name.text)
        #Cria o diretório destino se ele ainda não existe
        if os.path.isdir(dir + med_name):
            pass
        else:
            os.mkdir(dir + med_name)

        #plt.gcf()
        #plt.savefig(r'C:\Users\Joaodavi\Documents\Estágio\FRF_' + self.manager.get_screen('frf_wdw').ids.med_name.text + '\\frf_' + self.manager.get_screen('frf_wdw').ids.med_name.text + '_' + nome + '.pdf')

        # with open(r'C:\Users\Joaodavi\Documents\Estágio\FRF_' + self.manager.get_screen('frf_wdw').ids.med_name.text + '\\frf_' + self.manager.get_screen('frf_wdw').ids.med_name.text + '.csv', 'w', encoding='UTF8') as f:
        #
        #     writer = csv.writer(f)
        #
        #     writer.writerow(FRF)
        #
        #     writer.writerow(m_frf.freqVector)
        #
        #     writer.writerow(f_coere)
        #
        #     writer.writerow(coere)

        #Salva a medição em um arquivo .h5
        hf = h5py.File(dir + med_name + '\\frf_' + med_name + '.h5', 'w')
        g1 = hf.create_group('Dados')
        g1.create_dataset('FRF', data=sig_mon.FRF)
        g1.create_dataset('Vetor Frequência', data=sig_mon.m_frf.freqVector)
        g1.create_dataset('Vetor Coerência', data=sig_mon.f_coere)
        g1.create_dataset('Coerência', data=sig_mon.coere)

        plots_frf.save_plots((dir + med_name), ('\\frf_' + med_name + '.h5'))

