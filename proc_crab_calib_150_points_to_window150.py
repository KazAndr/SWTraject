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

sys.path.append(PACK_DIR)
from PRAO import *

files_0531 = sorted(
    glob.glob('./final_dataset' + os.sep + 'obs_data' + os.sep + '*'),
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

idx = 0
for name in tqdm(files_0531):
    head = read_head(name, 7)
    flat_obs = np.genfromtxt(name, skip_header=7)

    test_flat_obser = deepcopy(flat_obs)
    med_flux = np.median(test_flat_obser)

    i = 0

    while np.max(test_flat_obser) >= 1800:
        x_max = np.argmax(test_flat_obser)
        pulse = test_flat_obser[x_max - 25: x_max + 125] - med_flux
        i += 1

        medias = np.full(len(pulse), med_flux)
        test_flat_obser[x_max - 25: x_max + 125] = medias

        fName = './final_dataset/window150/' + head['date'] + '_plot_'+ head['name'] + '_'+ str(i)  + '.csv'
        head_file = 'name ' + head['name'] + '\n' + \
        'numpuls ' + str(1) + '\n' + \
        'tay ' + head['tay'] + '\n' + \
        'flux\n\n' # Добавление подписей колонок

        np.savetxt(fName, pulse, fmt='%1.3f', newline='\n', header=head_file, comments='')
        idx += 1
