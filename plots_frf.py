import h5py
import matplotlib.pyplot as plt
import numpy as np

def save_plots(path, name):
    frf_med = h5py.File(path + name, 'r')


    print(frf_med.keys())

    dados = frf_med.get('Dados')

    print(dados.keys())

    FRF = dados.get('FRF')
    f = dados.get('Vetor Frequência')
    coere = dados.get('Coerência')
    f_coere = dados.get('Vetor Coerência')
    print(FRF)
    print(f)

    FRF = np.array(FRF)
    print(FRF.shape)
    f = np.array(f)
    print(FRF)
    coere = np.array(coere)
    f_coere = np.array(f_coere)

    #Plota a resposta em frequência
    fig1 = plt.figure()
    frf_fig = fig1.subplots()
    frf_fig.semilogx(f, FRF[:, 0], label='Canal 1')
    frf_fig.semilogx(f, FRF[:, 1], label='Canal 2')
    frf_fig.set_title('Função resposta em frequência')
    frf_fig.set_xlabel('Frequência [Hz]')
    frf_fig.set_ylabel('Magnitude [dB]')
    frf_fig.legend()
    plt.savefig(path + '\\FRF.pdf')


    #Plota a coerência
    fig2 = plt.figure()
    coere_fig = fig2.subplots()
    coere_fig.semilogx(f_coere, coere[0])
    coere_fig.set_xlabel('Frequência [Hz]')
    coere_fig.set_ylabel('Coerência [-]')
    plt.savefig(path + '\\Coerência.pdf')

