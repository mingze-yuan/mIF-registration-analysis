from valis import registration
import os
from datetime import datetime
from time import time
from glob import glob
# from sys import argv

# src_dir = '/share/ymz/valisProject/data/mIF_175_organized'
src_dir = '/home/yuanmingze/data/mIF_20_organized'
# ls_crop = sorted(os.listdir('/public/share/ymz/valisProject/data/mIF_175_converted_cropped/images'), key=lambda x: int(x[1:]))
# ls_all = os.listdir('/public/share/ymz/valisProject/data/mIF_175_organized')
# patient_name_lst = sorted([x for x in ls_all if x not in ls_crop], key=lambda x: int(x[1:]))
# print(patient_name_lst)
dst_dir = '/home/yuanmingze/results/results_mIF_20'

# src_dir = '/home/yuanmingze/data/mIF_175_organized_debug'
# dst_dir = '/home/yuanmingze/results/results_mIF_175_debug'
# patient_name_lst = os.listdir(src_dir)
patient_name_lst = ['01019']
# patient_name_lst = [x for x in patient_name_lst if x != '01035']

def register_one_patient(patient_name: str):
    slide_src_dir = os.path.join(src_dir, patient_name)
    formatted_date = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    results_dst_dir = os.path.join(dst_dir, f"{patient_name}_{formatted_date}")
    os.makedirs(results_dst_dir, exist_ok=True)
    registered_slide_dst_dir = os.path.join(results_dst_dir, 'registered_slides')
    os.makedirs(registered_slide_dst_dir, exist_ok=True)
    
    # Create a Valis object and use it to register the slides in slide_src_dir
    registrar = registration.Valis(slide_src_dir, results_dst_dir, imgs_ordered=True, thumbnail_size=2048, series=2)
    rigid_registrar, non_rigid_registrar, error_df = registrar.register()
    
    # Perform micro-registration on higher resolution images, aligning *directly to* the reference image
    # registrar.register_micro(max_non_rigid_registration_dim_px=3000, align_to_reference=True)

    # Save all registered slides as ome.tiff
    registrar.warp_and_save_slides(registered_slide_dst_dir, crop="overlap", level=2)


if __name__ == '__main__':
    for patient_name in sorted(patient_name_lst):
        if len(glob(os.path.join(dst_dir, f"{patient_name}_*", 'registered_slides', '*'))) >= 5:
            print(f'---- Already finished registering {patient_name} ----')
            continue
        # patient_name = argv[1]
        print(f'---- Start registering {patient_name} ----')
        start_time = time()
        register_one_patient(patient_name)
        print(f'---- Finish registering {patient_name} with {time() - start_time:.2f}s ----')

    registration.kill_jvm()