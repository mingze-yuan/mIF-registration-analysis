from valis import registration
import pandas as pd
import os
from os.path import dirname, join, basename
import numpy as np
from glob import glob
from shutil import rmtree

src_dir = '/home/yuanmingze/results/results_mIF_175_after_crop'
cell_info_dir = '/home/yuanmingze/data/mIF_175_converted_cropped/cells_debug'
# crop_cfg_dir = '/public/share/ymz/valisProject/data/mIF_175_converted_cropped/configs'

# def get_cell_info_pth_from_ets_pth(ets_pth: str):
#     info_name = ets_pth.split('/')[-3]
#     # panel_name = 'P' + info_name.split('-')[-1][1] 
#     cell_info_pth_candid = glob(join(cell_info_dir, '*', 'cell seg data', f'{info_name[1:-1]}.vsi - 20x_01_cells.tsv'))
#     assert len(cell_info_pth_candid) == 1, f'Found {len(cell_info_pth_candid)} cell information tables'
#     return cell_info_pth_candid[0]

def warp_centroid_and_save(dir_name: str):
    patient_name = dir_name.split('_')[0]
    # print(patient_name)
    if patient_name != 'P103' and patient_name != 'P189':
        return
    print(patient_name)
    print(f"---- Start warping {patient_name} cell centroid ----")
    # regist_dir = join(src_dir, dir_name)
    regist_pth = join(src_dir, dir_name, patient_name, 'data', f'{patient_name}_registrar.pickle')
    assert os.path.exists(regist_pth), f"{patient_name} registrar not found at {regist_pth}"
    # regist_pth = '/home/yuanmingze/results/results_mIF_175/P1_2023-10-18-233335/P1/data/P1_registrar.pickle'
    result_dir = join(dirname(dirname(regist_pth)), 'warped_cell_centroid_debug')
    if os.path.exists(result_dir):
        rmtree(result_dir)
    os.makedirs(result_dir, exist_ok=True)

    print(f'---- Loading registrar ----')
    regist = registration.load_registrar(regist_pth)
    ori_img_list = regist.original_img_list
    num_ori_img = len(ori_img_list)
    print(f"Original image list with {num_ori_img} items:", regist.original_img_list)

    for idx, ori_img_pth in enumerate(ori_img_list):
        print(f"---- Loading slide object [{idx+1}/{num_ori_img}]----")
        # slide_obj = regist.get_slide('/share/ymz/valisProject/data/mIF_175_organized/P1/_Image_222476-P1-01_/stack1/frame_t.ets')
        slide_obj = regist.get_slide(ori_img_pth)
        print(f"---- Loading cell centroids [{idx+1}/{num_ori_img}]----")
        # cell_centroid_pth = '/share/ymz/valisProject/tmp/Image_222476-P1-01.vsi - 20x_01_cells.tsv'
        # cell_centroid_pth = get_cell_info_pth_from_ets_pth(ori_img_pth).re
        ori_img_name = basename(ori_img_pth)
        cell_centroid_pth = join(cell_info_dir, patient_name, ori_img_name.replace('.ome.tiff', '.csv'))
        # cell_centroid_pth = ori_img_pth.replace('.ome.tiff', '.csv')
        if not os.path.exists(cell_centroid_pth):
            print(f"Not found information at {cell_centroid_pth}")
            continue
        df_cell = pd.read_csv(cell_centroid_pth, usecols=['Centroid X µm', 'Centroid Y µm'])
        if len(df_cell) <= 10:
            print(f"Empty cell information at {cell_centroid_pth}")
            continue
        df_cell_before_crop = pd.read_csv(cell_centroid_pth, usecols=['Original Centroid X µm', 'Original Centroid Y µm'])
        original_xy_um = df_cell.to_numpy()
        original_xy_um_before_crop = df_cell_before_crop.to_numpy()
        um_per_px = slide_obj.reader.scale_physical_size(0)[0:2]
        print('Pixel width & height:', um_per_px)
        original_xy_px = original_xy_um / np.array(um_per_px)
        warped_xy_px = slide_obj.warp_xy(xy=original_xy_px, crop='overlap')
        warped_xy_um = warped_xy_px * np.array(um_per_px)

        print(f"---- Saving results [{idx+1}/{num_ori_img}]----")
        df_cell_warped = pd.DataFrame(np.concatenate((original_xy_um_before_crop, original_xy_um, original_xy_px, warped_xy_px, warped_xy_um), axis=1), 
                                      columns=['Centroid X µm', 'Centroid Y µm', 
                                               'Croped Centroid X µm', 'Croped Centroid Y µm', 'Croped Centroid X px', 'Croped Centroid Y px',
                                               'Warped Centroid X px', 'Warped Centroid Y px', 'Warped Centroid X µm', 'Warped Centroid Y µm'])
        dst_pth = join(result_dir, basename(cell_centroid_pth).replace('.csv', '_warped.csv'))
        df_cell_warped.to_csv(dst_pth, index=False)
        # df_cell_warped.to_csv(dst_pth, index=False, sep='\t')
        print(f"Saved at {dst_pth}")

if __name__ == '__main__':
    dir_name_lst = sorted(os.listdir(src_dir), key=lambda x: int(x[1:].split('_')[0]))
    # dir_name_lst = ['P103', 'P189']
    print(f"Prepared to warp {len(dir_name_lst)} patients: {dir_name_lst}")
    for dir_name in dir_name_lst:
        warp_centroid_and_save(dir_name)