import pandas as pd
import os
from glob import glob
from tqdm import tqdm

src_dir = '/home/yuanmingze/data/update_10/cell seg data'
src_pth_lst = glob(os.path.join(src_dir, '*', "*_cells.tsv"))
dst_dir = '/home/yuanmingze/data/update_10_converted_x_y_0301'
# src_pth = '/home/yuanmingze/data/update_10/cell seg data/P2/Image_222815-P1-02.vsi - 20x_01_cells.tsv'
for src_pth in tqdm(src_pth_lst):
    panel, fname = src_pth.split('/')[-2:]

    # dst_dir = '/share/pbao/SPEC-lightning/data_175_converted_1106_x_y'
    dst_pth = os.path.join(dst_dir, panel, 'cell seg data', fname)
    os.makedirs(os.path.dirname(dst_pth), exist_ok=True)

    info = pd.read_csv(src_pth, sep='\t', usecols=['Centroid X µm', 'Centroid Y µm'])
    info.to_csv(dst_pth, index=False, sep='\t')