from kivy.uix.screenmanager import Screen
from kivy.properties import ObjectProperty
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.animation import Animation
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
import matplotlib.pyplot as plt
import med_salas
import pytta
import os
import plots_sala
import h5py


class RevWindow(Screen):
    pass

class SigMonSala(Screen):
    label_in = []
    label_out = []
    def medicao(self):
        path = self.manager.get_screen('par_salas').ids

        lst_sala = [path.med_name.text, path.sinal.text, path.f_min.text, path.f_max.text, path.sample_rate.text,
                    path.fft_degree.text, path.num_ch_in.text, path.num_ch_out.text, path.out_amp.text, path.temp.text]
        #global med_sala, par_sala_media, resp_imp, flag, max_lvl_in, max_lvl_out

        self.med_sala, self.par_sala_media, self.resp_imp, self.flag, self.max_lvl_in, self.max_lvl_out = med_salas.par_salas(*lst_sala)


        return self.med_sala, self.par_sala_media, self.resp_imp, self.flag, self.max_lvl_in, self.max_lvl_out

    def on_enter(self, *args):
        SigMonSala.medicao(self)
        if self.flag == True:
            SigMonSala.set_levels(self)

    def set_levels(self):
        anim_lvl_in = []
        for n in range(len(self.max_lvl_in)):
            anim_lvl_in.append(int(300 + 5 * self.max_lvl_in[n]))

            SigMonSala.label_in.append(LabelIn(anim_height=anim_lvl_in[n]))
            self.manager.get_screen('sig_mon_sala').ids.box_bar.add_widget(SigMonSala.label_in[n])

        anim_lvl_out = int(300 + 5 * self.max_lvl_out)
        SigMonSala.label_out.append(LabelIn(anim_height=anim_lvl_out))
        #SigMonSala.animate(self, SigMonSala.label_out[0], anim_lvl_out)

        self.manager.get_screen('sig_mon_sala').ids.box_out.add_widget(SigMonSala.label_out[0])


        #print(type(sala_analise))
        self.manager.get_screen('sig_mon_sala').ids.box_out.children[0].text = (
                'Saída Canal 1: \n ' + str(round(self.max_lvl_out)) + ' [dBFS]')

        self.manager.get_screen('sig_mon_sala').ids.box_out.children[0].pos = self.width*.2, self.height*.01

        #Altera a cor das barras conforme o valor dBFS
        if self.max_lvl_out > 0:
            SigMonSala.label_out[0].rect_color.rgba = (1, 0, 0, 1)

        elif self.max_lvl_out > -5:
            SigMonSala.label_out[0].rect_color.rgba = (1, .4, .0, 1)

        elif -5 >= self.max_lvl_out >= -20:
            SigMonSala.label_out[0].rect_color.rgba = (0, 1, 0, 1)

        else:
            SigMonSala.label_out[0].rect_color.rgba = (.6, .4, .2, 1)

        #SigMonSala.animate(self, self.ids.box_out.children[0], anim_lvl_out)

        for j in range(len(self.max_lvl_in)):
            self.manager.get_screen('sig_mon_sala').ids.box_bar.children[j].text = (
                    'Entrada Canal ' + str(j+1) + ' : \n ' + '  ' + str(round(self.max_lvl_in[j])) + ' [dBFS]')

            self.manager.get_screen('sig_mon_sala').ids.box_bar.children[j].pos = self.width*.3*(1+j), self.height*.01

            #SigMonSala.animate(self, self.ids.box_bar.children[j], anim_lvl_in[j])

            #Altera as cores das barras conforme o valor dBFS

            if self.max_lvl_in[j] > 0:
                SigMonSala.label_in[j].rect_color.rgba = (1, 0, 0, 1)
                self.manager.get_screen('sig_mon_sala').ids.box_in.children[j].text = (
                        'Entrada Canal ' + str(j + 1) + ' : \n ' + '  ' + str(round(self.max_lvl_in[j])) + ' [dBFS] \n'
                        + 'OCORREU CLIPPING!!!')

            elif self.max_lvl_in[j] > -5:
                SigMonSala.label_in[j].rect_color.rgba = (1, .4, .0, 1)

            elif -5 >= self.max_lvl_in[j] >= -20:
                SigMonSala.label_in[j].rect_color.rgba = (0, 1, 0, 1)

            else:
                SigMonSala.label_in[j].rect_color.rgba = (.6, .4, .2, 1)


    def segue(self):
        if isinstance(self.par_sala_media, str):
            self.manager.current = 'warning'
        else:
            self.manager.current = 'select_plot'


    def animate(self, widget, anim_lvl):

        anim = Animation(anim_height=anim_lvl)
        anim.start(widget)


    def remove(self):
        self.manager.get_screen('sig_mon_sala').ids.box_out.remove_widget(SigMonSala.label_out[0])

        for n in range(int(self.manager.get_screen('par_salas').ids.num_ch_in.text)):
            self.manager.get_screen('sig_mon_sala').ids.box_bar.remove_widget(SigMonSala.label_in[n])


class LabelIn(Label):
    def __init__(self, anim_height, **kwargs):
        super(LabelIn, self).__init__(**kwargs)
        self.anim_height = anim_height


        with self.canvas.before:
            Color(.5, .8, .6, mode='rgb')
            self.rectf = Rectangle(pos=(self.width*5, self.height*7), size=(100, 80))

        with self.canvas:
            self.rect = Rectangle(pos=self.pos, size=(40, 0), group='ret')


        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)

    def update_rect(self, *args):
        self.rectf.pos = self.center_x-100, self.center_y-30
        self.rectf.size = 190, 65
        self.rect.pos = (self.center_x - 20), self.height*.65
        self.rect.size = (40, self.anim_height)


class LevelsSala(Screen):
    pass



class SalaPlot1(Screen):
    box = ObjectProperty()
    conta = 0
    val_par = []
    def add_plot(self, param):
        sig_mon = self.manager.ids.sig_mon_sala
        if param=='T20':
            self.fig1 = plots_sala.plot_T20(sig_mon.par_sala_media['Bandas'], sig_mon.par_sala_media['T20'])
        elif param=='EDT':
            self.fig1 = plots_sala.plot_EDT(sig_mon.par_sala_media['Bandas'], sig_mon.par_sala_media['EDT'])
        elif param=='T30':
            plots_sala.plot_T30(sig_mon.par_sala_media['Bandas'], sig_mon.par_sala_media['T30'])
        elif param=='C80':
            self.fig1 = plots_sala.plot_C80(sig_mon.par_sala_media['Bandas'], sig_mon.par_sala_media['C80'])
        elif param=='D50':
            self.fig1 = plots_sala.plot_C80(sig_mon.par_sala_media['Bandas'], sig_mon.par_sala_media['D50'])
        elif param=='RI':
            self.fig1 = sig_mon.resp_imp.plot_time(decimalSep='.')
        elif param=='Time':
            self.fig1 = plots_sala.time_plot(sig_mon.med_sala.timeVector, sig_mon.med_sala.timeSignal)
            #fig1 = med_par_sal.plot_time(decimalSep='.', title='Resposta no domínio do tempo', yLabel='Amplitude [-]')
        elif param=='Freq':
            self.fig1 = plots_sala.freq_plot(sig_mon.med_sala.freqVector, sig_mon.med_sala.freqSignal)
            #fig1 = med_par_sal.plot_freq(decimalSep='.', title='Resposta no domínio da frequência', yLabel='Amplitude [-]')
        elif param=='Spect':
            self.fig1 = sig_mon.med_sala.plot_spectrogram(decimalSep='.')
        elif param=='STel':
            self.fig1 = sig_mon.med_sala.plot_STearly(decimalSep='.')
        elif param=='STlt':
            self.fig1 = sig_mon.med_sala.plot_STlate(decimalSep='.')

        self.fig1 = plt.gcf()
        #self.box.add_widget(FigureCanvasKivyAgg(self.fig1))
        return self.fig1

    def on_pre_enter(self, *args):
        print(SalaPlot1.val_par)
        #self.fig1 = SalaPlot1.add_plot(self, SalaPlot1.val_par[0])
        #self.box.add_widget(FigureCanvasKivyAgg(self.fig1))
        SalaPlot1.forward(self, -1)

    def clear(self):
        if len(SalaPlot1.val_par) != 0:
            self.box.remove_widget(FigureCanvasKivyAgg(self.fig1))
            self.box.clear_widgets()
        else:
            pass

        plt.close('all')
    def forward(self, conta):
        SalaPlot1.conta = int(conta) + 1

        if SalaPlot1.conta <= (len(SalaPlot1.val_par)-1):
            self.fig1 = SalaPlot1.add_plot(self, SalaPlot1.val_par[SalaPlot1.conta])
            self.box.add_widget(FigureCanvasKivyAgg(self.fig1))
            print(SalaPlot1.conta)

        else:

            self.manager.current = 'primeira'
            print('fim')

    def backward(self, conta):
        SalaPlot1.conta = int(conta) - 1

        if SalaPlot1.conta >= 0:
            self.fig1 = SalaPlot1.add_plot(self, SalaPlot1.val_par[SalaPlot1.conta])
            self.box.add_widget(FigureCanvasKivyAgg(self.fig1))

        elif SalaPlot1.conta == len(SalaPlot1.val_par) - 1:
            SalaPlot1.conta = SalaPlot1.conta - 1

        else:
            print('Volta')
            self.manager.current = "select_plot"
        print(SalaPlot1.conta)

    def save(self):
        sig_mon = self.manager.ids.sig_mon_sala
        #dir = (r'C:\Users\Joaodavi\Documents\Estágio\SAGUI\Acústica_Salas_')
        dir = ('~/Desktop/Resultados/Resultados_')

        med_name = str(self.manager.get_screen('par_salas').ids.med_name.text)
        if os.path.isdir(dir + med_name):
            pass
        else:
            os.mkdir(dir + med_name)
        pytta.save((dir + med_name + "\\med_salas_" + med_name + ".hdf5"), sig_mon.med_sala)

        hf = h5py.File(dir + med_name + '\\par_media_' + med_name + '.h5', 'w')
        g1 = hf.create_group('Dados')
        g1.create_dataset('T20', data=sig_mon.par_sala_media['T20'])
        g1.create_dataset('T30', data=sig_mon.par_sala_media['T30'])
        g1.create_dataset('EDT', data=sig_mon.par_sala_media['EDT'])
        g1.create_dataset('C80', data=sig_mon.par_sala_media['C80'])
        g1.create_dataset('D50', data=sig_mon.par_sala_media['D50'])
        g1.create_dataset('Bandas', data=sig_mon.par_sala_media['Bandas'])

        plots_sala.save_plots((dir + med_name), ('\\par_media_' + med_name + '.h5'))


class SelectPlot(Screen):

    def checkbox_click(self, instance, value, parameter):
        if value == True:
            print(parameter)
            #fig1 = SalaPlot1.add_plot(self,parameter)
            SalaPlot1.val_par.append(parameter)

        elif value == False:
            SalaPlot1.val_par.remove(parameter)

    def on_pre_enter(self, *args):
        path_ck = self.manager.get_screen('select_plot').ids
        path_ck.ck_t20.active = True

    def on_pre_leave(self, *args):
        if len(SalaPlot1.val_par)==0:
            print("Algum valor deve ser selecionado")
            self.manager.current = 'primeira'

    def set_active(self):
        path_ck = self.manager.get_screen('select_plot').ids
        if path_ck.ck_all.active is True:
            path_ck.ck_time.active = True
            path_ck.ck_freq.active = True
            path_ck.ck_spec.active = True
            path_ck.ck_ri.active = True
            path_ck.ck_edt.active = True
            path_ck.ck_t20.active = True
            path_ck.ck_t30.active = True
            path_ck.ck_c80.active = True
            path_ck.ck_d50.active = True
            path_ck.ck_ste.active = True
            path_ck.ck_stl.active = True

        elif path_ck.ck_all.active is False:
            path_ck.ck_time.active = False
            path_ck.ck_freq.active = False
            path_ck.ck_spec.active = False
            path_ck.ck_ri.active = False
            path_ck.ck_edt.active = False
            path_ck.ck_t20.active = False
            path_ck.ck_t30.active = False
            path_ck.ck_c80.active = False
            path_ck.ck_d50.active = False
            path_ck.ck_ste.active = False
            path_ck.ck_stl.active = False

class Warning(Screen):
    pass

