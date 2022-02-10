import pytta
import scipy as scp
import numpy as np

def frf(med_name, sinal, f_min, f_max, SR, FFTdg, out_amp, num_ch_in, num_ch_out, temp):
    flag_FRF = False
    SR = int(SR)
    FFTdg = float(FFTdg)
    out_amp = float(out_amp)
    inCh = list(range(1, int(num_ch_in)+1))
    outCh = list(range(1, int(num_ch_out)+1))

    temp = float(temp)
    T = temp + 273  # Passa temperatura para Kelvin
    kf = 0.026  # Condutividade térmica do ar
    Po = 101325  # Pressão atmosférica no nível do mar [Pa]
    U_ar = 80  # Umidade relativa do ar
    visc = 7.72488e-8 * T - pow(5.95238e-11 * T, 2) + pow(2.71368e-14 * T, 3)  # Viscosidade
    R = 287.031  # Constante de gases (Ar)
    Rvp = 461.521  # Constante de gases (Vapor d'Agua)
    Pvp = 0.0658 * pow(T, 3) - 53.7558 * pow(T, 2) + 14703.8127 * T - 1345485.0465  # Pierce(Acoustics, 1991)
    cp = 4168.8 * ((0.249679) - (7.55179 * pow(10, -5) * T) + (1.69194 * pow(10, -7) * pow(T, 2)) - (
                6.46128 * pow(10, -11) * pow(T, 3)))  # Calor específico à pressão constante
    Cv = cp - R  # Calor específico a volume constante
    Pr = visc * cp / kf  # Número de Prandtl
    gamma = cp / Cv
    rho0 = Po / (R * T) - (1 / R - 1 / Rvp) * U_ar / 100 * Pvp / T
    global c0
    c0 = pow((gamma * Po / rho0), 0.5)
    Z = rho0 * c0


    if sinal == "Sweep":
        sinal_excit = pytta.generate.sweep(fftDegree=FFTdg, samplingRate=SR)

    elif sinal == "Ruído Branco":
        sinal_excit = pytta.generate.random_noise(kind='white', fftDegree=FFTdg, samplingRate=SR)

    elif sinal == "Ruído Rosa":
        sinal_excit = pytta.generate.random_noise(kind='pink', fftDegree=FFTdg, samplingRate=SR)

    elif sinal == "Seno":
        sinal_excit = pytta.generate.sin(fftDegree=FFTdg, samplingRate=SR)

    Med_FRF = pytta.generate.measurement(kind='playrec', samplingRate=SR, freqMin=f_min, freqMax=f_max,
                                          inChannels=inCh, outChannels=outCh, device=1, excitation=sinal_excit,
                                          outputAmplification=out_amp)

    m_FRF = Med_FRF.run()


    coere = []
    for n in range(len(inCh)):
        freq_coere, cohere = scp.signal.coherence(m_FRF.timeSignal[:, n], sinal_excit.timeSignal[:, 0], fs=SR, nfft=pow(2, 16),
                                                 window='hann', nperseg=1024, detrend='constant')

        coere.append(cohere)

    FRF = m_FRF.freqSignal/sinal_excit.freqSignal

    FRF_dB = 20*np.log10(abs(FRF)/(2*pow(10, -5))) - 94

    # Avalia os níveis de entrada e saída
    max_lvl_in = []
    for n in range(len(inCh)):
        max_lvl_in.append(pytta.classes.measurement._print_max_level(m_FRF[n], kind='input'))

    max_lvl_out = pytta.classes.measurement._print_max_level(sinal_excit, kind='output',
                                                             gain=(10 ** ((out_amp + .45) / 20)))


    flag_FRF = True

    return FRF_dB, m_FRF, freq_coere, coere, flag_FRF, max_lvl_in, max_lvl_out