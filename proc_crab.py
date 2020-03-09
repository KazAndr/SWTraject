"""
Выделение в отколиброванных данных импульсов пульсара в крабовидной туманности
превышающийх определенный предел по пиковой плотности потока. Сохраняются только изображения и файлы. 
НИкакие параметры импульсов(кроме пиковой плотности) не определяются. Для ускорения обработки. 
"""

import os
import sys
import glob
from copy import deepcopy
import datetime
import platform

import matplotlib.pyplot as plt
import numpy as np

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

files_0531 = sorted(
    glob.glob(f'.{os.sep}obs_data_real_calib{os.sep}*'),
    key=lambda x: datetime.datetime.strptime(os.path.basename(x),
                                             '%Y.%m.%d_obs_0531+21.csv')
)

for name in tqdm(files_0531):
    head = read_head(name, 7)
    day, month, year = head['date'].split('.')
    flat_obs = np.genfromtxt(name, skip_header=7)
    med_flux = np.median(flat_obs)
    std_obs = np.std(flat_obs)
    
    test_flat_obser = deepcopy(flat_obs)
    
    i = 0
    
    while np.max(test_flat_obser) >= (10*std_obs + med_flux):
        x_max = np.argmax(test_flat_obser)
        pulse = test_flat_obser[x_max - 25: x_max + 125] - med_flux
        
        path_pulse = (
                f'./results_set/plot_untypized/'
                f'{year}.{month}.{day}_plot_{head["name"]}_{i}.png'
            )
        
        fName = (
                f'./results_set/file_untypized/'
                f'{year}.{month}.{day}_plot_{head["name"]}_{i}.csv'
            )
        
        
        plt.close()
        plt.title('Session of observation of Crab in ' + head['date'] + ' ' + '№' + str(i))
        plt.xlabel('Number of point, dt = ' + head['tay']  + ' ' + 'ms')
        plt.ylabel('Flux density, ADC units')
        plt.plot(pulse)
        plt.savefig(path_pulse, format='png', dpi=100)
        
        head_file = (
                f'name {head["name"]}\n'
                f'numpuls {i}\n'
                f'tay {head["tay"]}\n'
                f'flux\n\n'
            )  # Добавление подписей колонок

        np.savetxt(fName, pulse, fmt='%1.3f',
                   newline='\n', header=head_file, comments='')
        
       
        test_flat_obser[x_max - 25: x_max + 125] = np.full(len(pulse), med_flux)
        
        i += 1
