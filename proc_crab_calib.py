import os
import sys
import glob
from copy import deepcopy
import datetime
import platform

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from tqdm import tqdm

if 'Windows' in platform.platform() and '8.1' in platform.release():
    _ = "C:\\Users\\Andrey\\YandexDisk\\3.Programing\\"
    DATA_DIR = _ + "work\\PulseViewer\\pulsarsData\\"
    PATTERN_DIR = _ + "work\\PulseViewer\\frame_of_AP\\patterns\\"
    PACK_DIR = _ + "myPacks\\"
    DELIMITER = "\\"

elif 'Windows' in platform.platform() and '7' in platform.release():
    _ = "E:\\Disk.Yandex\\3.Programing\\"
    DATA_DIR = "work\\PulseViewer\\pulsarsData\\"
    PATTERN_DIR = _ + "work\\PulseViewer\\frame_of_AP\\patterns\\"
    PACK_DIR = _ + "myPacks\\"
    DELIMITER = "\\"

elif 'Windows' in platform.platform() and '10' in platform.release():
    _ = "F:\\YandexDisk\\3.Programing\\"
    DATA_DIR = _ + "work\\PulseViewer\\pulsarsData\\"
    PATTERN_DIR = _ + "work\\PulseViewer\\frame_of_AP\\patterns\\"
    PACK_DIR = _ + "myPacks\\"
    ALL_DATA = "F:\\YandexDisk\\1.Работа\\Результаты обработки\\"
    DELIMITER = "\\"

elif 'Linux' in platform.platform() and '4.4.0' in platform.release():
    _ = "/home/andr/Yandex.Disk/3.Programing/"
    DATA_DIR = _ + "work/PulseViewer/pulsarsData/"
    PATTERN_DIR = _ + "/work/PulseViewer/frame_of_AP/patterns/"
    PACK_DIR = _ + "myPacks/"
    ALL_DATA = "/home/andr/Yandex.Disk/1.Работа/Результаты обработки/"
    DELIMITER = "/"

else:
    print('unknown system', platform.platform(), platform.release())

TEST_PIC = _ + 'test_pic'
sys.path.append(PACK_DIR)
from PRAO import *

gp_crab = pd.DataFrame(columns=[
    'Date',
    'Time start',
    'Tay, ms',
    'Period, s',
    'Numpointwin, point',
    'Numpulse, a.u.',
    'Median, adc u',
    'STD, adc u',
    'path obs plot',
    'path obs data',
    'Count of GP, u',
    'point of gp, point',
    'amp of gp, adc u',
    'W50, point',
    'W10, point',
    'path plot',
    'fName',

])

files_0531 = sorted(
    glob.glob('.\\obs_data\\*'),
    key=lambda x: datetime.datetime.strptime(os.path.basename(x), '%d.%m.%Y_obs_0531+21.csv'))

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

gp_pat = np.loadtxt(
            PATTERN_DIR
            + os.sep
            + 'GP_0531+21_2.4576'
            + '.csv',  skiprows=4)

idx = 0
for name in tqdm(files_0531):
    head = read_head(name, 7)
    flat_obs = np.genfromtxt(name, skip_header=7)

    med_flux_no_calib = np.median(flat_obs)
    test_flat_obser = deepcopy(flat_obs)
    test_flat_obser = test_flat_obser - med_flux_no_calib
    test_flat_obser = test_flat_obser + 1720
    std_obs = np.std(test_flat_obser)
    med_flux = np.median(test_flat_obser)

    fName_plot =  './obs_plot/' + head['date'] + '_plot_'+ head['name'] + '.png'
    plt.close()
    plt.plot(test_flat_obser) #[24150:24300]
    plt.axhline(med_flux, color='r')
    plt.axhline(med_flux + 10*std_obs, color='red')
    plt.axhline(med_flux - 3*std_obs, color='red')
    plt.savefig(fName_plot, format='png', dpi=100)

    fName_hist =  './hist_plot/' + head['date'] + '_hist_'+ head['name'] + '.png'
    bins = np.linspace(np.min(test_flat_obser), np.max(test_flat_obser), 1000)
    plt.close()
    plt.title('Distribution of pulses of Crab observation in ' + head['date'])
    plt.xlabel('Flux density, ADC units')
    plt.ylabel('Number of pulses')
    plt.hist(test_flat_obser, bins)
    plt.axvline(med_flux, color='r')
    plt.axvline(med_flux + 10*std_obs, color='red')
    plt.axvline(med_flux - 3*std_obs, color='red')
    plt.savefig(fName_hist, format='png', dpi=100)

    # ploting and writing session of observation

    i = 0

    while np.max(test_flat_obser) >= 1800:
        x_max = np.argmax(test_flat_obser)
        pulse = test_flat_obser[x_max - 10: x_max + 90] - med_flux

        path_pulse = './gp_plot/' + head['date'] + '_plot_'+ head['name'] + '_'+ str(i)  + '.png'
        plt.close()
        plt.title(
                'Session of observation of Crab in '
                + head['date']
                + ' '
                + '№'
                + str(i))

        plt.xlabel('Number of point, dt = ' + head['tay']  + ' ' + 'ms')
        plt.ylabel('Flux density, ADC units')
        plt.plot(pulse)
        plt.savefig(path_pulse, format='png', dpi=100)

        i += 1

        w10, _, _ =  width_of_pulse(pulse, 0.1)
        w50, _, _ = width_of_pulse(pulse, 0.5)

        amp = max(pulse)
        medias = np.full(len(pulse), med_flux)
        test_flat_obser[x_max - 10: x_max + 90] = medias

        fName = './gp_plot_txt/' + head['date'] + '_plot_'+ head['name'] + '_'+ str(i)  + '.csv'

        gp_crab.loc[idx] = [
            head['date'],
            head['time'],
            head['tay'],
            head['period'],
            head['numpointwin'],
            head['numpuls'],
            med_flux,
            std_obs,
            fName_plot,
            name,
            1,
            x_max,
            amp,
            w50,
            w10,
            path_pulse,
            fName,
        ]


        fName = './gp_plot_txt/' + head['date'] + '_plot_'+ head['name'] + '_'+ str(i)  + '.csv'
        head_file = 'name ' + head['name'] + '\n' + \
        'numpuls ' + str(1) + '\n' + \
        'tay ' + head['tay'] + '\n' + \
        'flux\n\n' # Добавление подписей колонок

        np.savetxt(fName, pulse, fmt='%1.3f', newline='\n', header=head_file, comments='')
        idx += 1

gp_crab.to_csv('crab_gp_kaz_10_2010-2018_calib.csv',  sep='\t', header=True, index=False)
