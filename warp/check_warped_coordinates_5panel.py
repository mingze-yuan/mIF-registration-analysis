import os
from tqdm import tqdm

data_dir = '/home/yuanmingze/results/warped_coordinate_mIF_175'

lst_folder = os.listdir(data_dir)
for folder in tqdm(lst_folder):
    if len(os.listdir(os.path.join(data_dir, folder))) != 5:
        print(folder, len(os.listdir(os.path.join(data_dir, folder))))