import matplotlib.pyplot as plt
import h5py
import numpy as np

def plot(dx, dy, ylabel, title):
    fig1 = plt.figure()
    axes = fig1.subplots()
    axes.plot(dx, dy)
    axes.set_title(title)
    axes.set_ylabel(ylabel)
    axes.set_xlabel('Frequência [Hz]')
    return fig1

def subplot(f, TF, f_coere, coere):
    fig2 = plt.figure()
    H12 = fig2.add_subplot(211)
    H12.plot(f, TF)
    H12.set_xlim([20, 1000])
    H12.set_title('Função de transferência entre as duas configurações')
    H12.set_ylabel("Magnitude [dB]")
    H12.set_xlabel("Frequência [Hz]")

    H12 = fig2.add_subplot(212)
    H12.plot(f_coere, coere)
    H12.set_xlim([20, 1000])
    H12.set_ylabel('Coerência')
    return fig2

def save(path, name):
    tubo = h5py.File(path + name, 'r')
    dados = tubo.get('Dados')

    f = dados.get('Freq')
    f = np.array(f)

    H_12 = dados.get('Função Transferência')
    H_12 = np.array(H_12)
    TF_1_2 = plot(f, H_12, '', 'Função de transferência entre as duas configurações')
    TF_1_2.savefig(path + '\\H_12.pdf')

    H_c = dados.get('Calibração')
    H_c = np.array(H_c)
    HC_1_2 = plot(f, H_c, '', 'Calibração')
    HC_1_2.savefig(path + '\\H_c.pdf')

    alpha = dados.get('Coef_Abs')
    alpha = np.array(alpha)
    f_alpha = dados.get('Freq_Abs')
    f_alpha = np.array(f_alpha)
    coef_abs = plot(f_alpha, alpha, '\u03B1 [-]', 'Coeficiente de absorção')
    coef_abs.savefig(path + '\\Coeficiente_absorção.pdf')
