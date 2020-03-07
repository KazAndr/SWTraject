#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 18 01:36:32 2019

@author: andr
"""

import os
import sys
import platform

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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

gp_table = pd.read_table('crab_gp_kaz_10_2010-2018_calib.csv', sep='\t')


for indx, row in tqdm(gp_table.iterrows()):
    pulse = np.loadtxt(row['fName'], skiprows=4)
    intersection_05 = np.argwhere(np.diff(np.sign(pulse - 0.5*np.max(pulse)))).flatten()
    pulses_05 = len(intersection_05)/2

    plt.close()
    plt.title(str(row['W50, point']) + ' ' + str(row['W10, point']))
    plt.plot(pulse)

    if np.mean(pulse[-5:]) == 0 or np.mean(pulse[:5]) == 0:
        plt.savefig('./trash/' + row['Date'] + '_plot_' + str(indx) + '.png',
                    format='png')
    elif pulses_05 > 9 or pulses_05 < 1:
        plt.savefig('./trash/' + row['Date'] + '_plot_' + str(indx) + '.png',
                    format='png')
    elif int(row['W10, point']) == 99 or int(row['W50, point']) == 99:
        plt.savefig('./trash/' + row['Date'] + '_plot_' + str(indx) + '.png',
                    format='png')
    elif int(row['W50, point']) < 10:
        plt.savefig('./trash/' + row['Date'] + '_plot_' + str(indx) + '.png',
                    format='png')
    elif int(row['W10, point']) < 10:
        plt.savefig('./trash/' + row['Date'] + '_plot_' + str(indx) + '.png',
                    format='png')
    else:
        plt.savefig('./pulses/' + row['Date'] + '_plot_' + str(indx) + '.png',
                    format='png')
