import os
import glob

from shutil import copyfile

files = sorted(glob.glob('./to_pulse/*'))

for name in files:
    name_file = os.path.basename(name)
    day, month, year = name_file[:10].split('.')

    path = './sorted/' + year + os.sep + month + os.sep

    if not os.path.exists(path):
        os.makedirs(path)

    copyfile(name, path + name_file)
