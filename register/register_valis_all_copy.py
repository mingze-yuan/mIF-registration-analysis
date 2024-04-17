from valis import registration
import os
from datetime import datetime
from time import time
from glob import glob


src_dir = '/share/ymz/valisProject/data/mIF_175_organized'
patient_name_lst = sorted(os.listdir(src_dir))
# dst_dir = '/home/yuanmingze/results/mIF_175'
# ls_skip = ['5']
patient_name_lst = ['P5']
dst_dir = '/share/ymz/valisProject/results_modified'
# results_dst_dir = os.path.join("/home/yuanmingze/results", os.path.basename(slide_src_dir) + f'_{formatted_date}')

def register_one_patient(patient_name: str):
    slide_src_dir = os.path.join(src_dir, patient_name)
    formatted_date = datetime.now().strftime('%Y-%m-%d-%H%M%S')
    results_dst_dir = os.path.join(dst_dir, f"{patient_name}_{formatted_date}")
    os.makedirs(results_dst_dir, exist_ok=True)
    registered_slide_dst_dir = os.path.join(results_dst_dir, 'registered_slides')
    os.makedirs(registered_slide_dst_dir, exist_ok=True)
    
    # Create a Valis object and use it to register the slides in slide_src_dir
    registrar = registration.Valis(slide_src_dir, results_dst_dir, imgs_ordered=True, thumbnail_size=2048)
    rigid_registrar, non_rigid_registrar, error_df = registrar.register()
    
    # Perform micro-registration on higher resolution images, aligning *directly to* the reference image
    registrar.register_micro(max_non_rigid_registration_dim_px=3000, align_to_reference=True)

    # Save all registered slides as ome.tiff
    registrar.warp_and_save_slides(registered_slide_dst_dir, crop="overlap", level=2)


if __name__ == '__main__':
    for patient_name in sorted(patient_name_lst, key=lambda x: int(x[1:])):
        # if patient_name == 'P120':
        #     continue
        # try:
        if len(glob(os.path.join(dst_dir, f"{patient_name}_*", 'registered_slides', '*'))) >= 5:
            print(f'---- Already finished registering {patient_name} ----')
            continue
        print(f'---- Start registering {patient_name} ----')
        start_time = time()
        register_one_patient(patient_name)
        print(f'---- Finish registering {patient_name} with {time() - start_time:.2f}s ----')
        # except:
        #     continue
    registration.kill_jvm()
    # Kill the JVM
