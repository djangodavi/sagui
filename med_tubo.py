import pytta
import numpy as np
import scipy as scp



def tubo_imp(med_name, sinal, SR, FFTdg, out_amp, tub_diam, temp, dist_mic, dist_amst, L_amst, gap_amst):
    SR = int(SR)
    FFTdg = float(FFTdg)
    out_amp = float(out_amp)
    tub_diam = float(1000*tub_diam)
    temp = float(temp)
    dist_mic = float(1000*dist_mic)
    dist_amst = float(1000*dist_amst)
    global x1
    x1 = dist_mic + dist_amst
    L_amst = float(1000*L_amst)
    gap_amst = float(1000*gap_amst)

    NFFT = pow(2, FFTdg)
    flag = False
    T = temp + 273  # Passa temperatura para Kelvin
    kf = 0.026  # Condutividade térmica do ar
    Po = 101325  # Pressão atmosférica no nível do mar [Pa]
    U_ar = 80  # Umidade relativa do ar
    visc = 7.72488e-8 * T - pow(5.95238e-11 * T, 2) + pow(2.71368e-14 * T, 3)  # Viscosidade
    R = 287.031  # Constante de gases (Ar)
    Rvp = 461.521  # Constante de gases (Vapor d'Agua)
    Pvp = 0.0658 * pow(T, 3) - 53.7558 * pow(T, 2) + 14703.8127 * T - 1345485.0465  # Pierce(Acoustics, 1991)
    cp = 4168.8 *((0.249679) - (7.55179 * pow(10, -5) * T) + (1.69194 * pow(10, -7) * pow(T, 2)) - (6.46128 * pow(10, -11) * pow(T, 3)))  # Calor específico à pressão constante
    Cv = cp - R       #Calor específico a volume constante
    Pr = visc*cp/kf   #Número de Prandtl
    gamma = cp/Cv
    rho0 = Po/(R*T)-(1/R-1/Rvp)*U_ar/100*Pvp/T
    global c0
    c0 = pow((gamma*Po/rho0), 0.5)
    Z = rho0*c0


    ## Setup Medição
    f_min = 0.05*c0/dist_mic
    f_max = 0.45*c0/dist_mic
    f_corte = 1.84*c0/np.pi



    if sinal == "Ruído Branco":
        sinal_excit = pytta.generate.random_noise(kind='white', fftDegree=FFTdg)

    elif sinal == "Sweep":
        sinal_excit = pytta.generate.sweep(fftDegree=FFTdg)
    else:
        print("Escolha o sinal")
    Med_tubo = pytta.generate.measurement(kind='playrec', samplingRate=SR, freqMin=f_min, freqMax=f_max,
                                          inChannels=[1, 2], outChannels=[1], device=1,
                                          excitation=sinal_excit, outputAmplification=out_amp)
    #time.sleep(3)
    med_direta = Med_tubo.run()

    global f
    f, S_yy_A1 = scp.signal.csd(med_direta.timeSignal[:, 0], med_direta.timeSignal[:, 0], fs=SR, nfft=pow(2, 16), nperseg=1024)
    #f, S_yy_A2 = scp.signal.csd(med_direta.timeSignal[:, 1], med_direta.timeSignal[:, 1], fs=SR, nfft=256, window='hann', return_onesided=False)

    f_xy, S_xy_A  = scp.signal.csd(med_direta.timeSignal[:, 0], med_direta.timeSignal[:, 1], fs=SR, nfft=pow(2, 16), nperseg=1024)
    #f_yx, S_yx_A  = scp.signal.csd(med_direta.timeSignal[:, 1], med_direta.timeSignal[:, 0], fs=SR, nfft=256, window='hann', return_onesided=False)

    f_xx, S_xx_rb = scp.signal.csd(sinal_excit.timeSignal[:, 0], sinal_excit.timeSignal[:, 0], fs=SR, nfft=pow(2, 16), nperseg=1024)
    #f_cross, S_xy_rb = scp.signal.csd(sinal_excit.timeSignal[:, 0], med_direta.timeSignal[:, 0], fs=SR, nfft=256, window='hann', return_onesided=False)
    #f_cross2, S_yx_rb = scp.signal.csd(sinal_excit.timeSignal[:, 0], med_direta.timeSignal[:, 1], fs=SR, nfft=256, window='hann', return_onesided=False)


    #fpsd, psd_w = scp.signal.welch(med_direta.timeSignal[:,0], fs=SR, nfft=256, window='hann', nperseg=None, detrend='constant', return_onesided=False, scaling='density', axis=- 1, average='mean')

    #def tfe(x,y,*args, **kwargs):
    #    a = np.asarray(csd(y, x, *args, *kwargs))
    #    b = np.asarray(psd(x, **kwargs))
    #   return a/b

    #TF = tfe(sinal_excit.timeSignal[:, 0], med_direta.timeSignal[:, 1])
    #f_vec = sinal_excit.freqVector
    #TF = scp.signal.TransferFunction(sinal_excit.timeSignal[:, 0], med_direta.timeSignal[:, 1])
    H12_A = S_xy_A/S_yy_A1
    freq_coere, coere = scp.signal.coherence(med_direta.timeSignal[:, 0], med_direta.timeSignal[:, 1], fs=SR, nfft=pow(2, 16), window='hann', nperseg=1024, detrend='constant')
    coherence = pow(abs(S_xy_A),2)/(S_xx_rb*S_yy_A1)
    max_lvl_in = []

    for n in range(2):
        max_lvl_in.append(pytta.classes.measurement._print_max_level(med_direta[n], kind='input'))

    max_lvl_out = pytta.classes.measurement._print_max_level(sinal_excit, kind='output', gain=10**(out_amp/20))

    flag = True
    return med_direta, f_xy, H12_A, freq_coere, coere, flag, max_lvl_in, max_lvl_out

def transfer_function(H12_A, H12_B):
    Hc = np.sqrt(H12_A / H12_B)
    H12 = np.sqrt(H12_A * H12_B)
    # Cálculo do número de onda para se obter o coeficiente de absorção
    k = f / c0

    r = ((H12 - np.imag(H12))/(np.real(H12) - H12))*np.exp(2*1j*k*x1)

    alpha = 1 - pow(abs(r),2)

    Z_specif = (1+r)/(1-r)   #Z/(rho0*c0)


    return H12, Hc, alpha, f



