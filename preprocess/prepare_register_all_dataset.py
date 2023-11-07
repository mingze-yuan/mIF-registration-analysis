import os
from shutil import copy, copytree
from glob import glob
from time import time
from os.path import join, isfile, basename
from multiprocessing import Pool
from tqdm import tqdm

# src_dir = '/home/yuanmingze/data/mIF_175'
src_dir = '/share/chenzifan/PBN202200225FW_20/全景图'
dst_dir = '/home/yuanmingze/data/mIF_20_organized'
# dst_dir = '/public/share/ymz/valisPdroject/data/mIF_175_organized'
patient_lst = [x.split('-')[-2] for x in os.listdir('/share/chenzifan/PBN202200225FW_20/全景图/P1') if x.endswith('.vsi')]
# print(sorted(patient_lst, key=lambda x: int(x[1:])))
# print(len(patient_lst))

def copy_one_patient(patient_name: str):
    start_time = time()
    dst_base_dir = join(dst_dir, patient_name)
    os.makedirs(dst_base_dir, exist_ok=True)
    src_pth_ls = glob(join(src_dir, '*', f'*-{patient_name}-*'))
    # if len(src_pth_ls) != 10:
        # print(patient_name, len(src_pth_ls))
    # assert len(src_pth_ls) == 10, f"Unmatched files for {patient_name} with{src_pth_ls}!"
    for src_pth in src_pth_ls:
        if isfile(src_pth):
            copy(src_pth, join(dst_base_dir, basename(src_pth)))
        else:
            copytree(src_pth, join(dst_base_dir, basename(src_pth)))
    print(f"[{patient_name}] Time elapsed: {time() - start_time:.2f}s")

if __name__ == '__main__':
    for patient_name in tqdm(patient_lst):
        copy_one_patient(patient_name)
    # with Pool(8) as p:
    #     p.map(copy_one_patient, patient_lst)