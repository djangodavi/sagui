import pytta
import numpy as np
import time

def nps_terco(med_name, sinal, f_min, f_max, SR, FFTdg, out_amp, num_ch_in, num_ch_out):
    flag_des = False
    f_min = float(f_min)
    f_max = float(f_max)
    num_ch_in = int(num_ch_in)
    num_ch_out = int(num_ch_out)
    SR = int(SR)
    FFTdg = float(FFTdg)
    out_amp = float(out_amp)
    inCh = list(range(1, num_ch_in+1))
    outCh = list(range(1, num_ch_out+1))
    print(inCh, outCh)

    #inCh = [1, 2]
    #outCh = [1]

    if sinal == "Ruído Branco":
        sinal_excit = pytta.generate.random_noise(kind='white', fftDegree=FFTdg, samplingRate=SR)

    elif sinal == "Ruído Rosa":
        sinal_excit = pytta.generate.random_noise(kind='pink', fftDegree=FFTdg, samplingRate=SR)



    M = pytta.generate.measurement(kind='playrec', samplingRate=SR, freqMin=f_min, freqMax=f_max, excitation=sinal_excit,
                                   inChannels=inCh, outChannels=outCh, device=1, outputAmplification=out_amp)

    med_des = M.run()

    filtro = pytta.generate.octfilter(nthOct=3, samplingRate=SR, minFreq=f_min, maxFreq=f_max)

    max_lvl_in = []
    for n in range(len(inCh)):
        max_lvl_in.append(pytta.classes.measurement._print_max_level(med_des[n], kind='input'))

    max_lvl_out = pytta.classes.measurement._print_max_level(sinal_excit, kind='output',
                                                             gain=(10 ** ((out_amp + .45) / 20)))

    ##
    med_filt = filtro(med_des)

    print('center', filtro.center, 'min_freq', filtro.minFreq, 'min_band', filtro.minBand)
    print('max_freq', filtro.maxFreq, 'max_band', filtro.maxBand)

    numBand = filtro.maxBand - filtro.minBand
    print("Número de bandas:", numBand)

    bandas = filtro.center
    #print(len(lista_bandas))

    nps = med_des.spl()
    print(nps)


    ini = time.time()
    mat_nps = np.ones((len(inCh), len(bandas)))

    for m in range(0, len(inCh)):
        for n in range(0, len(bandas)):
            mat_nps[m, n] = mat_nps[m, n]*med_filt[m][n].spl()

    media_nps = mat_nps.mean(0) #média entre os microfones

    flag_des = True
    fim = time.time()
    #print("Tempo decorrido", fim-ini)
    return media_nps, med_des, bandas, flag_des, max_lvl_in, max_lvl_out

#nps_terco(med_name='t', sinal="Ruído Branco", f_min=50, f_max=5000, SR=44100, FFTdg=18, out_amp=-3)

def calcula_dn(nps_e, nps_r, T20_r):
    TR_ref = (np.ones(len(T20_r)))*0.5
    Dn = nps_e - nps_r
    Dnt = Dn + 10*np.log10(T20_r/TR_ref)

    return Dnt

def calcula_dntw(Dnt):
    Dnt_calc = np.array(Dnt[:16])
    # Curva de referência ISO 717-1
    curva_ref = np.array([33, 36, 39, 42, 45, 48, 51, 52, 53, 54, 55, 56, 56, 56, 56, 56])
    difs = curva_ref - Dnt_calc

    # while np.sum(difs) > 32:
    #     for n in range(len(curva_ref)):
    #         difs[n] = curva_ref[n] - Dnt_calc[n]
    #
    #         if difs[n] > 0:
    #             curva_ref[n] = curva_ref[n] - 1
    #         else:
    #             pass
    #     difs = curva_ref - Dnt_calc

    while np.sum(difs) > 32:
        curva_ref = curva_ref - 1
        difs = curva_ref - Dnt_calc

    return curva_ref
