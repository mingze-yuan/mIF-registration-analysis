import os
from shutil import copytree
from tqdm import tqdm

src_dir = '/home/yuanmingze/results/results_mIF_20'
dst_dir = '/home/yuanmingze/results/warped_coordinate_mIF_20'

patient_folder_lst = os.listdir(src_dir)
# error_lst = ['P1', 'P2', "P142", 'P98', 'P100', 'P124', 'P144', 'P147', 'P165', 'P177']
# error_lst = ['P103', 'P189']
for patient_folder in tqdm(patient_folder_lst):
    patient_name = patient_folder.split('_')[0]
    # if patient_name not in error_lst:
    #     continue
    print(patient_name)
    dst_base_dir = os.path.join(dst_dir, patient_name)
    # os.makedirs(dst_base_dir, exist_ok=True)
    copytree(os.path.join(src_dir, patient_folder, patient_name, 'warped_cell_centroid_debug'), dst_base_dir, dirs_exist_ok=True)
# data_dir = '/public/share/ymz/valisProject/data/mIF_175_organized'
# data_lst = os.listdir(data_dir)
# dst_lst = os.listdir(dst_dir)

# print([x for x in data_lst if x not in dst_lst])