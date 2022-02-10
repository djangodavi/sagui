from kivy.uix.screenmanager import Screen
from kivy.garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.graphics import Rectangle, Color
import med_desempenho
import med_salas
import matplotlib.pyplot as plt
import os
import h5py


class DesempenhoWindow(Screen):
    pass

class SigMonDes(Screen):
    #global conta
    #conta = 0
    label_in = []
    label_out = []

    def __init__(self, **kwargs):
        super(SigMonDes, self).__init__(**kwargs)
        self.conta = 0
    #    self.media_nps, self.med_des, self.bandas, self.flag_des, self.max_lvl_in, self.max_lvl_out = med_desempenho.nps_terco(*self.lst_des)

    def med_des(self):
        path = self.manager.get_screen('desemp_wdw').ids

        lst_des = [path.med_name.text, path.sinal.text, path.f_min.text, path.f_max.text, path.sample_rate.text,
                        path.fft_degree.text, path.out_amp.text, path.num_ch_in.text, path.num_ch_out.text]

        self.media_nps, self.med_des, self.bandas, self.flag_des, self.max_lvl_in, self.max_lvl_out = med_desempenho.nps_terco(*lst_des)

        return self.media_nps, self.med_des, self.bandas, self.flag_des, self.max_lvl_in, self.max_lvl_out

    def on_enter(self, *args):
        self.conta = self.conta + 1

        if self.conta == 1:

            self.emissora = SigMonDes.med_des(self)

            if self.emissora[3] == True:
                SigMonDes.set_levels(self)


        elif self.conta == 2:

            self.receptora = SigMonDes.med_des(self)

            if self.receptora[3] == True:
                SigMonDes.set_levels(self)


        elif self.conta == 3:
            m_sala, room_par_media, flag2, max_lvl_in, max_out  = med_salas.par_salas(med_name=self.manager.get_screen('desemp_wdw').ids.med_name.text, sinal='Sweep',
                                                                                      f_min=int(self.manager.get_screen('desemp_wdw').ids.f_min.text), f_max=int(self.manager.get_screen('desemp_wdw').ids.f_max.text),
                                                                                      sample_rate=44100, fft_degree=18, num_ch_in=self.manager.get_screen('desemp_wdw').ids.num_ch_in.text,
                                                                                      num_ch_out=self.manager.get_screen('desemp_wdw').ids.num_ch_out.text, out_amp=-3, temp=20)


            self.Dnt = med_desempenho.calcula_dn(self.emissora[0], self.receptora[0], room_par_media)

            # Curva de referência ISO 717-1
            self.curva_ref = [33, 36, 39, 42, 45, 48, 51, 52, 53, 54, 55, 56, 56, 56, 56, 56]

            self.curva_ajus = med_desempenho.calcula_dntw(self.Dnt)

            if flag2 == True:
                SigMonDes.set_levels(self)
            self.conta = 0


    def zera_cont(self):
        self.conta = 0

    def set_levels(self):
        anim_lvl_in = []
        for n in range(len(self.max_lvl_in)):
            anim_lvl_in.append(int(300 + 5 * self.max_lvl_in[n]))

            SigMonDes.label_in.append(LabelIn(anim_height=anim_lvl_in[n]))
            self.manager.get_screen('sig_mon_des').ids.box_in.add_widget(SigMonDes.label_in[n])

        anim_lvl_out = int(300 + 5 * self.max_lvl_out)
        SigMonDes.label_out.append(LabelIn(anim_height=anim_lvl_out))
        #SigMonSala.animate(self, SigMonSala.label_out[0], anim_lvl_out)

        self.manager.get_screen('sig_mon_des').ids.box_out.add_widget(SigMonDes.label_out[0])


        #print(type(sala_analise))
        self.manager.get_screen('sig_mon_des').ids.box_out.children[0].text = (
                'Saída Canal 1: \n ' + str(round(self.max_lvl_out)) + ' [dBFS]')

        self.manager.get_screen('sig_mon_des').ids.box_out.children[0].pos = self.width*.2, self.height*.01

        #Altera a cor das barras conforme o valor dBFS
        if self.max_lvl_out > 0:
            SigMonDes.label_out[0].rect_color.rgba = (1, 0, 0, 1)

        elif self.max_lvl_out > -5:
            SigMonDes.label_out[0].rect_color.rgba = (1, .4, .0, 1)

        elif -5 >= self.max_lvl_out >= -20:
            SigMonDes.label_out[0].rect_color.rgba = (0, 1, 0, 1)

        else:
            SigMonDes.label_out[0].rect_color.rgba = (.6, .4, .2, 1)

        #SigMonDes.animate(self, self.ids.box_out.children[0], anim_lvl_out)

        for j in range(len(self.max_lvl_in)):
            self.manager.get_screen('sig_mon_des').ids.box_in.children[j].text = (
                    'Entrada Canal ' + str(j+1) + ' : \n ' + '  ' + str(round(self.max_lvl_in[j])) + ' [dBFS]')

            self.manager.get_screen('sig_mon_des').ids.box_in.children[j].pos = self.width*.3*(1+j), self.height*.01

            #SigMonSala.animate(self, self.ids.box_bar.children[j], anim_lvl_in[j])

            #Altera as cores das barras conforme o valor dBFS

            if self.max_lvl_in[j] > 0:
                SigMonDes.label_in[j].rect_color.rgba = (1, 0, 0, 1)
                self.manager.get_screen('sig_mon_des').ids.box_in.children[j].text = (
                        'Entrada Canal ' + str(j + 1) + ' : \n ' + '  ' + str(round(self.max_lvl_in[j])) + ' [dBFS] \n'
                        + 'OCORREU CLIPPING!!!')

            elif self.max_lvl_in[j] > -5:
                SigMonDes.label_in[j].rect_color.rgba = (1, .4, .0, 1)

            elif -5 >= self.max_lvl_in[j] >= -20:
                SigMonDes.label_in[j].rect_color.rgba = (0, 1, 0, 1)

            else:
                SigMonDes.label_in[j].rect_color.rgba = (.6, .4, .2, 1)

    def segue(self):
        if self.conta == 1:
            self.manager.current = 'aviso'

        elif self.conta == 2:
            self.manager.get_screen(
                'aviso').ids.texto_aviso.text = 'Leve a FONTE para a sala RECEPTORA, \n para medição do Tempo de Reverberação. \n' \
                                                'Quando os equipamentos estiverem \n corretamente posicionados, clique em "OK".'
            self.manager.get_screen('aviso').rect.source = 'RUIDO_AEREO_SALA_EMISSAO.png'
            self.manager.current = 'aviso'

        elif self.conta == 3:
            self.manager.current = 'plot_wdw_des'
            self.conta = 0

    def decrementa(self):
        self.conta = self.conta - 1

        if self.conta == 0:
            self.manager.current = 'desemp_wdw'
            self.zera_cont()
        elif self.conta == 1:
            self.manager.current = 'aviso'

    def remove(self):
        self.manager.get_screen('sig_mon_des').ids.box_out.remove_widget(SigMonDes.label_out[0])

        for n in range(int(self.manager.get_screen('desemp_wdw').ids.num_ch_in.text)):
            self.manager.get_screen('sig_mon_des').ids.box_in.remove_widget(self.label_in[n])

class LabelIn(Label):
    def __init__(self, anim_height, **kwargs):
        super(LabelIn, self).__init__(**kwargs)
        self.anim_height = anim_height

        with self.canvas.before:
            Color(.5, .8, .6, mode='rgb')
            self.rectf = Rectangle(pos=(self.width*5, self.height*7), size=(100, 80))

        with self.canvas:
            self.rect_color = Color(rgba=(.49, .12, .7, 1))
            self.rect = Rectangle(pos=self.pos, size=(40, 0))


        self.bind(pos=self.update_rect)
        self.bind(size=self.update_rect)

    def update_rect(self, *args):
        self.rectf.pos = self.center_x-100, self.center_y-30
        self.rectf.size = 190, 65
        self.rect.pos = (self.center_x - 20), self.height*.65
        self.rect.size = (40, self.anim_height)


class Aviso(Screen):
    def __init__(self, **kwargs):
        super(Aviso, self).__init__(**kwargs)
        self.conta = 0
        with self.canvas.before:
            self.rect = Rectangle(source='RUIDO_AEREO_SALA_RECEPCAO.png')

    def on_pos(self, *args):
        self.rect.pos = self.pos

    def on_size(self, *args):
        self.rect.size = self.size

    def on_enter(self):
        self.conta = self.conta + 1

    def decrementa(self):
        sig_mon = self.manager.get_screen('sig_mon_des')
        sig_mon.zera_cont()


class PlotWindowDes(Screen):
    box = ObjectProperty()

    def add_plot(self, dx, dy, dy2):
        sig_mon = self.manager.ids.sig_mon_des
        fig1 = plt.figure()
        axes = fig1.subplots()
        axes.semilogx(dx[:16], dy[:16], label='Curva medida')
        axes.semilogx(sig_mon.bandas[:16], sig_mon.curva_ref, label="Curva ISO 717-7")
        axes.semilogx(sig_mon.bandas[:16], dy2, label='Curva ajustada')
        axes.set_xlabel('Frequência [Hz]')
        axes.set_ylabel('Dnt [dB]')
        axes.semilogx(sig_mon.bandas[7], dy2[7], color='red', marker='o', label=('Dntw = ' + str(dy2[7])))
        axes.legend()
        labels = ['100', '125', '160', '200', '250', '315', '400', '500', '630', '800',
                  '1000', '1250', '1600', '2000', '2500', '3150', '4000']
        axes.set_xticks(sig_mon.bandas[:16])
        axes.set_xticklabels(labels, rotation=45)

        self.fig1 = fig1
        return self.fig1

    def on_enter(self, *args):
        sig_mon = self.manager.ids.sig_mon_des
        self.fig1 = self.add_plot(sig_mon.bandas, sig_mon.Dnt, sig_mon.curva_ajus)
        self.box.add_widget(FigureCanvasKivyAgg(self.fig1))


    def clear(self):
        self.box.remove_widget(FigureCanvasKivyAgg(self.fig1))
        plt.close('all')

    def save(self):
        sig_mon = self.manager.ids.sig_mon_des
        #dir = (r'C:\Users\Joaodavi\Documents\Estágio\SAGUI\Desempenho_')
        dir = ('~/Desktop/Resultados/Resultados_')
        med_name = self.manager.get_screen('desemp_wdw').ids.med_name.text

        if os.path.isdir(dir + med_name):
            pass
        else:
            os.mkdir(dir + med_name)

        plt.gcf()
        plt.savefig(dir + med_name + '\desempenho_' + self.manager.get_screen('desemp_wdw').ids.med_name.text + '.pdf')

        # Salva a medição em um arquivo .h5
        hf = h5py.File(dir + med_name + '\\desempenho_' + med_name + '.h5', 'w')
        g1 = hf.create_group('Dados')
        g1.create_dataset('Curva Ajustada', data=sig_mon.curva_ajus)
        g1.create_dataset('Dnt', data=sig_mon.Dnt)
        g1.create_dataset('Bandas Frequência', data=sig_mon.bandas)
        g1.create_dataset('Curva Referência', data=sig_mon.curva_ref)
        g1.create_dataset('Dntw', data=sig_mon.curva_ajus[7])

