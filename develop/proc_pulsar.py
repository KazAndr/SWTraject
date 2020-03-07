import os
import sys
import glob
import copy
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

pulsar_name = '1112+50'
global_dir_pulsar = ALL_DATA + pulsar_name + os.sep

global_files = sorted(glob.glob(global_dir_pulsar + '20*' + os.sep + '*' + os.sep + '*_profiles.txt'))

sessons_obs = pd.DataFrame(columns=[
    'Date', 
    'Session'
])
gp_pulsar = pd.DataFrame(columns=[
    'Date', 
    'Time start', 
    'Tay, ms',
    'Period, s',
    'Numpointwin, point',
    'Numpulse, a.u.',
    'Median, adc u',
    'STD, adc u',
    'File name',
    'Count of GP, u',
    'Num pulse',
    'point of gp, point',
    'amp of gp, adc u',
    'W50, point',
    'W10, point',
    'path plot',
    
])
idx = 0
idx_obs = 0
for file in tqdm(global_files):
    try:
        head, main_profile, data_pulses, back = read_profiles(file)
        pattern = np.loadtxt(
            PATTERN_DIR
            + DELIMITER
            + head['name']
            + '_'
            + head['tay']
            + '.csv',  skiprows=4)
        
        l_edge, r_edge = edgesOprofile(main_profile, pattern)
        #thres = 30*np.max(main_profile)
        
        if quality_data(main_profile, l_edge, r_edge):
            sessons_obs.loc[idx_obs] = [
                head['date'],
                1
            ]
            idx_obs += 1
            
            for index, pulse in enumerate(data_pulses):
                noise = np.append(pulse[:l_edge], pulse[r_edge:])
                if (np.max(pulse) >= 10*np.std(noise)) and (l_edge <= np.argmax(pulse) <= r_edge):
                    
                    w10, _, _ =  width_of_pulse(pulse, 0.1)
                    w50, _, _ = width_of_pulse(pulse, 0.5)
                    
                    path_pulse = (
                        './gp_plot_pulsar/'
                        + head['date']
                        + '_plot_'
                        + head['name']
                        + '_'
                        + str(index)
                        + '.png')
                    
                    plt.close()
                    plt.title(
                        'Session of observation of '
                        + pulsar_name
                        +
                        ' in '
                        + head['date']
                        + ' '
                        + '№'
                        + str(index))
                    
                    plt.xlabel('Number of point, dt = ' + head['tay']  + ' ' + 'ms')
                    plt.ylabel('Flux density, ADC units')
                    plt.plot(pulse)
                    plt.savefig(path_pulse, format='png', dpi=100)
                    
                    gp_pulsar.loc[idx] = [
                        head['date'],
                        head['time'],
                        head['tay'],
                        head['period'],
                        head['numpointwin'],
                        head['numpuls'],
                        np.mean(back),
                        np.std(np.append(pulse[:l_edge], pulse[r_edge:])),
                        os.path.basename(file),
                        1,
                        index,
                        np.argmax(pulse),
                        np.max(pulse),
                        w50,
                        w10,
                        path_pulse
                    ]
                    idx += 1
                    
                else:
                    continue
        else:
            continue
            
    except ValueError:
        with open('valerr_' + pulsar_name + '.log', 'a') as f:
            f.write(os.path.basename(file))
            f.write('\n')
    except OSError:
        with open('oserr_' + pulsar_name + '.log', 'a') as f:
            f.write(os.path.basename(file))
            f.write('\n')

gp_pulsar.to_csv(pulsar_name + '_gp_kaz_10_sigma.csv',  sep='\t', header=True, index=False)
sessons_obs.to_csv(pulsar_name + '_obs_kaz_10_sigma.csv',  sep='\t', header=True, index=False)