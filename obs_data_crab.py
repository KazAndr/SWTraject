import os
import sys
import glob
import datetime
import platform

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

sys.path.append(PACK_DIR)
from PRAO import *

sessons_obs = pd.DataFrame(columns=[
    'Date',
    'Session'
])

files_0531 = glob.glob(ALL_DATA + '0531+21'
                       + DELIMITER + '*' + DELIMITER + '*' + DELIMITER
                       + '*_profiles.txt')
print('Main object: 0531+21; Numbers of files: ' + str(len(files_0531)))

# установка диапазона дат
date_start = datetime.datetime(2008, 11, 17, 0, 0)
data_stop = datetime.datetime(2019, 11, 18, 0, 0)

main_set = [x for x in files_0531
             if date_start <= datetime.datetime.strptime(os.path.basename(x)[:6], '%d%m%y') <= data_stop]
print('Main set: 0531+21; Numbers of files: ' + str(len(main_set)))

idx_obs = 0
for file_name in tqdm(main_set):
    try:
        head, main_pulse, data_pulses, back = read_profiles_MD(file_name)

        non_cor_data = []
        for pulse, backg in zip(data_pulses, back):
            non_cor_data.append(pulse + backg)
        obser = np.hstack(non_cor_data)

        diag = []
        for x in np.linspace(-1.3, 1.4, len(obser) + int(head['numpointwin'])):
            if x == 0:
                diag.append(1)
            else:
                diag.append((np.sin(x)/x)**2)

        cor_d = []
        for data_point, coeff in zip(obser, diag):
            cor_d.append(data_point/coeff)
        cor_d = np.asarray(cor_d)

        med_flux = np.median(cor_d)
        cor_d = cor_d.reshape(int(head['numpuls'])-1, int(head['numpointwin']))

        final_array = []
        for pulse in cor_d:
            l_edge = np.median(pulse[:6])
            r_edge = np.median(pulse[-5:])
            array_coef = np.linspace(l_edge, r_edge, len(pulse))

            coef_pulse = []
            for point, cf in zip(pulse, array_coef):
                coef_pulse.append(point-cf + med_flux)
            final_array.append(coef_pulse)
        final_array = np.asarray(final_array)
        flat_obser = np.hstack(final_array)
        #  writing session of observation
        fName = './obs_data/' + head['date'] + '_obs_' + head['name'] + '.csv'
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

sessons_obs.to_csv(
        'crab' + '_obs_kaz.csv',  sep='\t', header=True, index=False)
