import os
import sys
import glob
import datetime
import platform

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from tqdm import tqdm
from scipy import signal


def flatter(data, polynomialOrder=15):

    ## Применяем медианную фильтрацию с максимальным шагом:
    res_filter = signal.medfilt(data, kernel_size=29)
    # Фитируем получившийся массив:
    xData = range(len(res_filter))
    yData = res_filter
    # curve fit the data
    fittedParameters = np.polyfit(xData, yData, polynomialOrder)
    xModel = np.linspace(min(xData), max(xData), len(xData))
    yModel = np.polyval(fittedParameters, xModel)

    return yModel


def sinxx(x):
    return (np.sin(x)/x)**2


def beam_obs(x, amp,  shift, y0):
    return amp*(np.sin(x + shift)/(x + shift))**2 + y0


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

sys.path.append(PACK_DIR)
from PRAO import *

# Создание списка дат хороших дней
list_files = sorted(glob.glob('./good_days_full/*'))
date_list = [os.path.basename(i)[:10] for i in list_files]

sessons_obs = pd.DataFrame(columns=[
    'Date',
    'Session'
])

beam_coeff = pd.DataFrame(columns=[
    'Date',
    'A',
    'shift',
    'y0',
    'Jy/ADC'
])

files_0531 = glob.glob(ALL_DATA + '0531+21'
                       + DELIMITER + '*' + DELIMITER + '*' + DELIMITER
                       + '*_profiles.txt')
print('Main object: 0531+21; Numbers of files: ' + str(len(files_0531)))

# установка диапазона дат
date_start = datetime.datetime(2009, 11, 20, 0, 0)
data_stop = datetime.datetime(2019, 11, 18, 0, 0)

main_set = [x for x in files_0531
             if date_start <= datetime.datetime.strptime(os.path.basename(x)[:6], '%d%m%y') <= data_stop]
print('Main set: 0531+21; Numbers of files: ' + str(len(main_set)))

idx_obs = 0
for file_name in tqdm(main_set):
    try:
        head, main_pulse, data_pulses, back = read_profiles_MD(file_name)

        if head['date'] in date_list:

            non_cor_data = []
            for pulse, backg in zip(data_pulses, back):
                non_cor_data.append(pulse + backg)
            obser = np.hstack(non_cor_data)

            fullpoints = int(head['numpuls'])*int(head['numpointwin'])
            x = np.linspace(-1.37, 1.37, fullpoints)

            obspoints = fullpoints - int(head['numpointwin'])
            y = sinxx(x[:obspoints])

            x = x[:obspoints]
            poli = flatter(obser, 4)
            max_calib = max(poli)
            amp = max_calib
            shift = 0
            y0 = 50
            popt,pcov = curve_fit(beam_obs,x,obser,p0=[amp,shift, y0])
            
            beam_coeff = beam_obs(x,*popt)
            coeff = 1720/(amp - popt[2])
            obser = coeff*obser
            y0_back = popt[2]*coeff
            
            beam_coeff.loc[idx_obs] = [
                head['date'],
                popt[0],
                popt[1],
                popt[2],
                coeff,
            ]
            
            cor_d = []
            for data_point, coeff in zip(obser, poli/np.max(poli)):
                cor_d.append(data_point/coeff)
            cor_d = np.asarray(cor_d)


            poli_13 = flatter(cor_d, 13)
            flat_obser = (cor_d - poli_13) + np.median(cor_d)  # Калибровка
            med_flat_obser = np.median(flat_obser)
            # std_flat_obser = np.std(flat_obser)


            #  writing session of observation

            fName_plot =  './obs_plot_real_calib/' + head['date'] + '_plot_'+ head['name'] + '.png'

            plt.close()
            plt.subplot(311)
            plt.plot(obser)
            plt.plot(beam_coeff)
            plt.subplot(312)
            plt.plot(cor_d)
            plt.plot(poli_13, color='r')
            plt.subplot(313)
            plt.plot(flat_obser) #[24150:24300]
            plt.axhline(med_flat_obser, color='r')
            # plt.axhline(med_flat_obser - 3*std_flat_obser, color='red')
            plt.savefig(fName_plot, format='png', dpi=100)

            fName = './obs_data_real_calib/' + head['date'] + '_obs_' + head['name'] + '.csv'
            head_file = (
                'name ' + head['name'] + '\n'
                + 'date ' + head['date'] + '\n'
                + 'time ' + head['time'] + '\n'
                + 'period ' + head['period'] + '\n'
                + 'numpuls ' + head['numpuls'] + '\n'
                + 'tay ' + head['tay'] + '\n'
                + 'numpointwin ' + str(int(head["l_point_win"]) + 1) + '\n')

            np.savetxt(
                fName,
                flat_obser,
                fmt='%1.5f',
                delimiter='\t',
                newline='\n',
                header=head_file,
                comments='')
            
            sessons_obs.loc[idx_obs] = [
                    head['date'],
                    1
                ]
            idx_obs += 1

    except ValueError:
        with open('valerr_' + 'crab' + '.log', 'a') as f:
            f.write(os.path.basename(file_name))
            f.write('\n')
    except OSError:
        with open('oserr_' + 'crab' + '.log', 'a') as f:
            f.write(os.path.basename(file_name))
            f.write('\n')

sessons_obs.to_csv('crab_obs_kaz.csv',  sep='\t', header=True, index=False)

beam_coeff.to_csv('beam_coeff_obs_kaz.csv',  sep='\t', header=True, index=False)