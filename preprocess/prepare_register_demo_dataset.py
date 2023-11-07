import os
from shutil import copy, copytree
from glob import glob
from tqdm import tqdm

if __name__ == "__main__":
    src_dir = '/home/yuanmingze/data/mIF_175'
    dst_dir = '/home/yuanmingze/data/mIF_P1_demo_ets'
    os.makedirs(dst_dir, exist_ok=True)
    patient_name = 'P1'

    src_dir_ls = glob(os.path.join(src_dir, "*", f"*-{patient_name}-*", 'stack1', 'frame_t.ets'))
    print(src_dir_ls)
    
    for src_pth in tqdm(src_dir_ls):
        print(src_pth)
        frame_id = src_pth.split(f'-{patient_name}-')[-1][:2]
        # copy(src_pth, os.path.join(dst_dir, f'{patient_name}_{frame_id}.ets'))
        
    # for src_pth in tqdm(src_dir_ls):
    #     if os.path.isfile(src_pth):
    #         copy(src_pth, os.path.join(dst_dir, os.path.basename(src_pth)))
    #     else:
    #         copytree(src_pth, os.path.join(dst_dir, os.path.basename(src_pth)))