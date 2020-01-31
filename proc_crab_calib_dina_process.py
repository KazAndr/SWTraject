import os
import sys
import glob
import datetime
from copy import deepcopy
import datetime
import platform

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tqdm import tqdm
from sklearn.externals import joblib

if 'Windows' in platform.platform() and '8.1' in platform.release():
    _ = "C:\\Users\\Andrey\\YandexDisk\\3.Programing\\"
    DATA_DIR = _ + "work\\PulseViewer\\pulsarsData\\"
    PATTERN_DIR = _ + "work\\PulseViewer\\frame_of_AP\\patterns\\"
    PACK_DIR = _ + "myPacks\\"

elif 'Windows' in platform.platform() and '7' in platform.release():
    _ = "E:\\Disk.Yandex\\3.Programing\\"
    DATA_DIR = "work\\PulseViewer\\pulsarsData\\"
    PATTERN_DIR = _ + "work\\PulseViewer\\frame_of_AP\\patterns\\"
    PACK_DIR = _ + "myPacks\\"

elif 'Windows' in platform.platform() and '10' in platform.release():
    _ = "F:\\YandexDisk\\3.Programing\\"
    DATA_DIR = _ + "work\\PulseViewer\\pulsarsData\\"
    PATTERN_DIR = _ + "work\\PulseViewer\\frame_of_AP\\patterns\\"
    PACK_DIR = _ + "myPacks\\"
    ALL_DATA = "F:\\YandexDisk\\1.Работа\\Результаты обработки\\"

elif 'Linux' in platform.platform() and '4.4.0' in platform.release():
    _ = "/home/andr/Yandex.Disk/3.Programing/"
    DATA_DIR = _ + "work/PulseViewer/pulsarsData/"
    PATTERN_DIR = _ + "/work/PulseViewer/frame_of_AP/patterns/"
    PACK_DIR = _ + "myPacks/"
    ALL_DATA = "/home/andr/Yandex.Disk/1.Работа/Результаты обработки/"

else:
    print('unknown system', platform.platform(), platform.release())

sys.path.append(PACK_DIR)
from PRAO import *

loaded_model = joblib.load('dina_model_RFC(1000)_pulse_noise_95.sav')

def read_head(filename, numpar):
    header = {}
    with open(filename, 'r') as file:
        for i in range(numpar):
            a, *b = file.readline().split()
            try:
                header[a] = b[0] + '.' + b[1]
            except IndexError:
                header[a] = b[0].replace(',', '.')
    return header

gp_crab = pd.DataFrame(columns=[
    'Date',
    'Time start',
    'Tay, ms',
    'Period, s',
    'Numpointwin, point',
    'Numpulse, a.u.',
    'Median, Jy',
    'STD, Jy',
    'path obs data',
    'Count of GP, u',
    'point of gp, point',
    'amp of gp, Jy',
    'W50, point',
    'W10, point',
    'path plot',
    'fName',

])

sessons_obs = pd.DataFrame(columns=[
    'Date',
    'Session'
])

files_0531 = sorted(
    glob.glob(f'.{os.sep}obs_data_real_calib{os.sep}*'),
    key=lambda x: datetime.datetime.strptime(os.path.basename(x), '%Y.%m.%d._obs_0531+21.csv'))

idx = 0
for name in tqdm(files_0531):
    head = read_head(name, 7)
    flat_obs = np.genfromtxt(name, skip_header=7)
    
    sessons_obs.loc[idx] = [
        head['date'],
        1
    ]
    idx += 1

    test_flat_obser = deepcopy(flat_obs)
    med_flux = np.median(test_flat_obser)
    std_obs = np.std(test_flat_obser)
    
    i = 0

    while np.max(test_flat_obser) >= 1820:
        x_max = np.argmax(test_flat_obser)
        pulse = test_flat_obser[x_max - 25: x_max + 125] - med_flux
        if len(pulse) == 0:
            break

        n_pulse = pulse/max(pulse)

        if len(n_pulse) == 150:
            pass
        else:
            n_pulse = np.append(n_pulse, np.zeros(150 - len(n_pulse)))

        NN_decition = loaded_model.predict([n_pulse])
        if NN_decition[0] == 1:

            path_pulse = f'./final_dataset/gp_plot_real_calib/' + head['date'] + '_plot_'+ head['name'] + '_'+ str(i)  + '.png'
            plt.close()
            plt.title(
                    'Session of observation of Crab in '
                    + head['date']
                    + ' '
                    + '№'
                    + str(i))

            plt.xlabel('Number of point, dt = ' + head['tay']  + ' ' + 'ms')
            plt.ylabel('Flux density, Jy')
            plt.plot(pulse)
            plt.savefig(path_pulse, format='png', dpi=50)

            i += 1

            w10, _, _ =  width_of_pulse(pulse, 0.1)
            w50, _, _ = width_of_pulse(pulse, 0.5)

            amp = max(pulse)
            medias = np.full(len(pulse), med_flux)
            test_flat_obser[x_max - 25: x_max + 125] = medias

            fName = './final_dataset/gp_plot_txt_real_calib/' + head['date'] + '_plot_'+ head['name'] + '_'+ str(i)  + '.csv'

            gp_crab.loc[idx] = [
                head['date'],
                head['time'],
                head['tay'],
                head['period'],
                head['numpointwin'],
                head['numpuls'],
                med_flux,
                std_obs,
                name,
                1,
                x_max,
                amp,
                w50,
                w10,
                path_pulse,
                fName,
            ]

            head_file = 'name ' + head['name'] + '\n' + \
            'numpuls ' + str(1) + '\n' + \
            'tay ' + head['tay'] + '\n' + \
            'flux\n\n' # Добавление подписей колонок

            np.savetxt(fName, pulse, fmt='%1.3f', newline='\n', header=head_file, comments='')
            idx += 1
        else:
            medias = np.full(len(pulse), med_flux)
            test_flat_obser[x_max - 25: x_max + 125] = medias

now = datetime.datetime.now().strftime("%Y-%m-%d")
gp_crab.to_csv(f'crab_gp_kaz_10_2010-2019_calib_dina_{now}.csv',  sep='\t', header=True, index=False)
sessons_obs.to_csv(f'crab_obs_kaz_2010-2019_dina_{now}.csv',  sep='\t', header=True, index=False)