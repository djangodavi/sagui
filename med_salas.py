import pytta
import numpy as np

def par_salas(med_name, sinal, f_min, f_max, sample_rate, fft_degree, num_ch_in, num_ch_out, out_amp, temp):
    f_min = float(f_min)
    f_max = float(f_max)
    SR = float(sample_rate)
    fft_degree = float(fft_degree)
    out_amp = float(out_amp)
    temp = float(temp)
    flag = False
    inCh = list(range(1, int(num_ch_in)+1))
    print("canais de entrada", inCh)
    outCh = list(range(1, int(num_ch_out) + 1))

    if sinal == "Sweep":
        sinal_excit = pytta.generate.sweep(fftDegree=fft_degree)

    elif sinal == "Ruído Branco":
        sinal_excit = pytta.generate.random_noise(kind='white', fftDegree=fft_degree)

    elif sinal == "Ruído Rosa":
        sinal_excit = pytta.generate.random_noise(kind='pink', fftDegree=fft_degree)

    elif sinal == "Seno":
        sinal_excit = pytta.generate.sin(fftDegree=fft_degree)



    Med_sala = pytta.generate.measurement(kind='playrec', samplingRate=SR, freqMin=f_min, freqMax=f_max,
                                          inChannels=inCh, outChannels=outCh, device=1, excitation=sinal_excit,
                                          outputAmplification=out_amp)

    m_sala = Med_sala.run()

    filtro = pytta.generate.octfilter(nthOct=3)


    sala_flt = filtro(m_sala)
    sinal_flt = filtro(sinal_excit)

    #nps_sala_flt = sala_flt[1].spl()
    #nps_sinal_flt = sinal_flt[1].spl()

    print('nps_sala', sala_flt[0][3].spl(), 'nps_sala_banda2', sala_flt[0][13].spl(), 'nps_sinal', sinal_flt[0][2].spl())

    ##Cálculo da resposta impulsiva
    imp_res = pytta.classes.ImpulsiveResponse(excitation=sinal_excit, recording=m_sala)
    IR = []
    resp_imp = []
    room_par = []
    #room_par = list(range(2, 400))
    T20 = []
    T30 = []
    EDT = []
    C80 = []
    D50 = []

    for n in range(len(inCh)):
        IR.append(imp_res.IR[0].timeSignal[0:int(1*SR)])

        resp_imp.append(pytta.SignalObj(signalArray=IR[n], domain='time', samplingRate=SR))

        room_par.append(pytta.RoomAnalysis(resp_imp[n], nthOct=3, minFreq=100, maxFreq=8000))

        T20.append(room_par[n].T20)

        T30.append(room_par[n].T30)

        EDT.append(room_par[n].EDT)

        C80.append(room_par[n].C80)

        D50.append(room_par[n].D50)

    T20_media = sum(T20)/len(T20)

    T30_media = sum(T30)/len(T30)

    EDT_media = sum(EDT)/len(EDT)

    C80_media = sum(C80)/len(C80)

    D50_media = sum(D50)/len(D50)

    room_par_media = {'T20':T20_media, 'T30':T30_media, 'EDT':EDT_media, 'C80':C80_media, 'D50':D50_media, 'Bands':room_par[0].bands}
    max_lvl_in = []
    for n in range(len(inCh)):
        max_lvl_in.append(pytta.classes.measurement._print_max_level(m_sala[n], kind='input'))

    max_out = pytta.classes.measurement._print_max_level(sinal_excit, kind='output', gain=(10 ** ((out_amp+.45) / 20)))


    ##Condição para prever o erro do SNR muito baixo
    # squaredIR = resp_imp.timeSignal ** 2
    # # assume the last 10% of the IR is noise, and calculate its noise level
    # last10Idx = -int(len(squaredIR) // 10)
    # noiseLevel = np.mean(squaredIR[last10Idx:])
    # # get the maximum of the signal, that is the assumed IR peak
    # max_val = np.max(squaredIR)
    # max_idx = np.argmax(squaredIR)
    # # check if the SNR is enough to assume that the signal is an IR. If not,
    # # the signal is probably not an IR, so it starts at sample 1
    # idxNoShift = np.asarray([max_val < 100 * noiseLevel or
    #                          max_idx > int(0.9 * squaredIR.shape[0])])
    # # less than 20dB SNR or in the "noisy" part
    #
    #
    # if idxNoShift.any():
    #     room_par = 'SNR muito baixo! Ajuste os ganhos e realize uma nova medição.'
    # else:
    #
    #     #room_par = 'parametros de salas'


        #time_fig = plots.time_plot(m_sala.timeVector, m_sala.timeSignal)
    #room_par_media = sum(room_par)/len(room_par)
    #room_par_media = np.ones(18)*.5
    flag = True


    return m_sala, room_par_media, resp_imp, flag, max_lvl_in, max_out