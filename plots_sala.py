import matplotlib.pyplot as plt
import h5py
import numpy as np

def time_plot(time_vec, time_sig):
    time_fig = plt.figure()
    axes = time_fig.subplots(1,1)
    axes.plot(time_vec, time_sig)
    axes.set_xlabel("Tempo [s]")
    axes.set_ylabel("Amplitude [-]")
    axes.set_title("Sinal no domínio do tempo")
    return time_fig

def freq_plot(freq_vec, freq_sig):
    freq_fig = plt.figure()
    axes = freq_fig.subplots()
    axes.semilogx(freq_vec, freq_sig)
    axes.set_xlabel("Frequência [Hz]")
    axes.set_ylabel("Magnitude [-]")
    axes.set_title("Sinal no domínio da frequência")

    return freq_fig


def plot_T20(bandas, T20):
    vetor_pos = list(range(len(bandas)))
    t20_fig = plt.figure()
    axes = t20_fig.subplots()
    axes.bar(vetor_pos, T20)
    axes.set_xlabel("Frequência [Hz]")
    axes.set_ylabel("Tempo de reverberação [s]")
    axes.set_title("T20")
    axes.set_xticks(vetor_pos)
    axes.set_xticklabels(bandas)

    return t20_fig

def plot_T30(bandas, T30):
    vetor_pos = list(range(len(bandas)))
    t30_fig = plt.figure()
    axes = t30_fig.subplots()
    axes.bar(vetor_pos, T30)
    axes.set_xlabel("Frequência [Hz]")
    axes.set_ylabel("Tempo de reverberação [s]")
    axes.set_title("T30")
    axes.set_xticks(vetor_pos)
    axes.set_xticklabels(bandas)

    return t30_fig

def plot_EDT(bandas, EDT):
    vetor_pos = list(range(len(bandas)))
    EDT_fig = plt.figure()
    axes = EDT_fig.subplots()
    axes.bar(vetor_pos, EDT)
    axes.set_xlabel("Frequência [Hz]")
    axes.set_ylabel("Tempo de reverberação [s]")
    axes.set_title("EDT")
    axes.set_xticks(vetor_pos)
    axes.set_xticklabels(bandas)

    return EDT_fig

def plot_C80(bandas, C80):
    vetor_pos = list(range(len(bandas)))
    C80_fig = plt.figure()
    axes = C80_fig.subplots()
    axes.bar(vetor_pos, C80)
    axes.set_xlabel("Frequência [Hz]")
    axes.set_ylabel("C80")
    axes.set_title("Clareza")
    axes.set_xticks(vetor_pos)
    axes.set_xticklabels(bandas)

    return C80_fig

def plot_D50(bandas, D50):
    vetor_pos = list(range(len(bandas)))
    D50_fig = plt.figure()
    axes = D50_fig.subplots()
    axes.bar(vetor_pos, D50)
    axes.set_xlabel("Frequência [Hz]")
    axes.set_ylabel("D50 [%]")
    axes.set_title("Definição")
    axes.set_xticks(vetor_pos)
    axes.set_xticklabels(bandas)

    return D50_fig

def save_plots(path, name):
    t20_med = h5py.File(path + name, 'r')
    dados = t20_med.get('Dados')
    bandas = dados.get('Bandas')
    bandas = np.array(bandas)

    T20 = dados.get('T20')
    T20 = np.array(T20)
    t20_fig = plot_T20(bandas, T20)
    t20_fig.savefig(path + 'T20.pdf', dpi=100)

    T30 = dados.get('T30')
    T30 = np.array(T30)
    t30_fig = plot_T30(bandas, T30)
    t30_fig.savefig(path + 'T30.pdf', dpi=100)

    EDT = dados.get('EDT')
    EDT = np.array(EDT)
    edt_fig = plot_EDT(bandas, EDT)
    edt_fig.savefig(path + 'EDT.pdf', dpi=100)

    C80 = dados.get('C80')
    C80 = np.array(C80)
    c80_fig = plot_C80(bandas, C80)
    c80_fig.savefig(path + 'C80.pdf', dpi=100)

    D50 = dados.get('C80')
    D50 = np.array(D50)
    d50_fig = plot_D50(bandas, D50)
    d50_fig.savefig(path + 'D50.pdf', dpi=100)

