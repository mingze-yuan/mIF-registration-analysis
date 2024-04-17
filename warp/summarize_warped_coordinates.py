import pandas as pd
import os
from glob import glob
from tqdm import tqdm
from os.path import dirname, basename

res_dir = '/home/yuanmingze/results/results_mIF_175_after_crop'
res_csv_lst = sorted(glob(os.path.join(res_dir, '*', '*', 'warped_cell_centroid_updated', '*.csv')))
file_pths, patient_names, file_names, counts = [], [], [], []

for res_csv_pth in tqdm(res_csv_lst):
    res = pd.read_csv(res_csv_pth)
    patient_names.append(dirname(dirname(res_csv_pth)))
    file_names.append(basename(res_csv_pth))
    file_pths.append(res_csv_pth)
    counts.append(len(res))

sum_info = pd.DataFrame({'file_pth': file_pths, 'patient': patient_names, 'file': file_names, 'count': counts})
sum_info.to_excel('/home/yuanmingze/tmp/res_sum_mIF_175_with_crop.xlsx', index=False)


