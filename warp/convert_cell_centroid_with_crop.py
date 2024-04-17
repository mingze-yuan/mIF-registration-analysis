from valis import slide_io
from json import load
from shutil import rmtree
import os
from os.path import join
from glob import glob
import pandas as pd
import numpy as np
from typing import Union

# cfg_dir = '/share/ymz/valisProject/data/mIF_175_converted_cropped/configs'
cfg_dir = '/home/yuanmingze/data/mIF_175_converted_cropped/configs'
output_dir = '/home/yuanmingze/data/mIF_175_converted_cropped/cells_debug'
cell_info_dir = '/share/pbao/SPEC-lightning/data_175_converted_1106_x_y'
# cell_info_dir = '/home/yuanmingze/data/update_10_converted_x_y_0301'
series, level = 2, 0
case_error_lst = []


def extract_points(bbox: Union[list, tuple], points: np.array):
    assert len(bbox) == 4
    assert points.shape[1] == 2
    x, y, w, h = bbox
    box_start = np.array([x, y])
    box_end = np.array([x + w, y + h])
    mask = np.all((points >= box_start) & (points < box_end), axis=1)
    extracted_points = points[mask]
    new_coords = extracted_points - box_start
    return extracted_points, new_coords

def get_cell_info_pth_from_ets_pth(ets_pth: str):
    info_name = ets_pth.split('/')[-3]
    cell_info_pth_candid = glob(join(cell_info_dir, '*', 'cell seg data', f'{info_name[1:-1]}.vsi - 20x_*_cells.tsv'))
    assert len(cell_info_pth_candid) == 1, f'Found {len(cell_info_pth_candid)} cell information tables for {ets_pth}'
    return cell_info_pth_candid[0]

def compute_centroid_after_crop(patient_name: str):
    print(f"---- Start computing {patient_name} cell centroids ----")
    cfg = load(open(os.path.join(cfg_dir, patient_name + '.json'), 'r'))
    source_lst, processed_lst, bbox_all_lst = cfg['source'], cfg['processed'], cfg['bbox']
    output_info_dir = os.path.join(output_dir, patient_name)
    # if os.path.exists(output_info_dir) and len(os.listdir(output_info_dir)) >= 5:
    #     print(f'Already converted coordinates for {patient_name}')
    #     return
    if os.path.exists(output_info_dir):
        rmtree(output_info_dir)
    os.makedirs(output_info_dir, exist_ok=True)
    
    for pi, (source, processed, bbox_all) in enumerate(zip(source_lst, processed_lst, bbox_all_lst)):
        # try:
        # Get reader for slide format
        print(source)
        reader_cls = slide_io.get_slide_reader(source, series=series) #Get appropriate slide reader class
        reader = reader_cls(source, series=series) # Instantiate reader

        # Get size of images and physical size of per pixel
        print(reader.metadata.slide_dimensions)
        pyramid_level_sizes_wh = reader.metadata.slide_dimensions[level]
        print(f'\n[{pi+1}/{len(source_lst)}] Image weight & height:', pyramid_level_sizes_wh)
        img_width, img_height = pyramid_level_sizes_wh
        um_per_px = reader.metadata.pixel_physical_size_xyu[:2]
        img_width_physical, img_height_physical = img_width * um_per_px[0], img_height * um_per_px[1]
        print(f'[{pi+1}/{len(source_lst)}] Pixel width & height:', um_per_px)

        # get original cell centroids  
        cell_centroid_pth = get_cell_info_pth_from_ets_pth(source)
        print(f'[{pi+1}/{len(source_lst)}] Loading cell centroids from:', cell_centroid_pth)
        df_cell = pd.read_csv(cell_centroid_pth, sep='\t', usecols=['Centroid X µm', 'Centroid Y µm'])
        original_xy_um = df_cell.to_numpy()
        print(f'[{pi+1}/{len(source_lst)}] Number of cell centroids:', len(original_xy_um))

        # get bounding box
        fname = os.path.basename(processed).removesuffix('.png')
        for idx, bbox in enumerate(bbox_all):
            bbox = [0, 0, 1, 1]
            x, y, w, h = bbox
            xywh = (x*img_width_physical, y*img_height_physical, w*img_width_physical, h*img_height_physical)
            print(original_xy_um)
            extracted_points, crop_xy_um = extract_points(bbox=xywh, points=original_xy_um)
            if crop_xy_um.shape[0] > 10:
                print(f"---- ({idx+1}/{len(bbox_all)}) Extracted {crop_xy_um.shape[0]} points from the bounding box {xywh}")
                df_cell_crop = pd.DataFrame(
                    np.concatenate([extracted_points, crop_xy_um], axis=1), 
                    columns=['Original Centroid X µm', 'Original Centroid Y µm', 'Centroid X µm', 'Centroid Y µm'])
                cropped_position_pth= os.path.join(output_info_dir, f"{fname}-{idx+1}.csv")
                df_cell_crop.to_csv(cropped_position_pth, index=False)
        # except:
        #     case_error_lst.append([patient_name, pi, (source, processed, bbox_all)])

if __name__ == '__main__':
    # patient_name_lst = sorted([x.removesuffix('.json') for x in os.listdir(cfg_dir)], key=lambda x: int(x[1:]))
    patient_name_lst = ['P103', 'P189']
    for patient_name in patient_name_lst:
        # if patient_name == 'P5':
        #     continue
        compute_centroid_after_crop(patient_name)
    slide_io.kill_jvm()

    print(case_error_lst)