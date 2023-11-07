import os
from valis import slide_io
from typing import Union
from utils import convert_ets_to_ometiff, get_foreground_original_area, find_connected_components, bounding_box, find_pairs, merge_pair_masks
from glob import glob
from tqdm import tqdm
import numpy as np
import cv2
from matplotlib import patches
import matplotlib.pyplot as plt
from pandas import DataFrame
import json
from sys import argv


def judge_duplicated(patient_name: str, data_dir: str, runs_dir: str):
    slide_src_f_lst = glob(os.path.join(data_dir, patient_name, f'*-{patient_name}-*', 'stack1', 'frame_t.ets'))
    process_img_f_lst = glob(os.path.join(runs_dir, f"{patient_name}_*", f"{patient_name}", 'processed', '*.png'))
    assert len(slide_src_f_lst) == 5
    assert len(process_img_f_lst) == 5
    slide_src_f_lst = sorted(slide_src_f_lst, key=lambda x: x.split('/')[-3].split('-')[-1])
    process_img_f_lst = sorted(process_img_f_lst)
    original_area_lst = [get_foreground_original_area(slide_src_f, process_img_f) for slide_src_f, process_img_f in zip(slide_src_f_lst, process_img_f_lst)]
    print(f"{patient_name}: {original_area_lst}")
    duplicated_flag = bool(np.max(original_area_lst) > 1.8 * np.min(original_area_lst))
    duplicated_idx = [idx for idx, original_area in enumerate(original_area_lst) if original_area > 1.8 * np.min(original_area_lst)]
    return duplicated_flag, duplicated_idx, process_img_f_lst, slide_src_f_lst

if __name__ == '__main__':
    # data_dir = '/share/ymz/valisProject/data/mIF_175_organized'
    data_dir = '/home/yuanmingze/data/mIF_20_organized'
    runs_dir = '/share/ymz/valisProject/results_modified_20'
    # runs_dir = '/share/ymz/valisProject/results_modified_reverse'
    patient_name_lst = [argv[1]]
    # patient_name_lst = [x.split('_')[0] for x in os.listdir(runs_dir)]
    # lst_all_img_f, lst_all_src_f, lst_bbox_all = [], [], []

    for patient_name in sorted(patient_name_lst, key=lambda x : int(x[1:])):
        duplicated_flag, duplicated_idx, process_img_f_lst, slide_src_f_lst = judge_duplicated(patient_name, data_dir, runs_dir)
        print(patient_name, duplicated_flag, duplicated_idx, process_img_f_lst, slide_src_f_lst)
        output_dir = os.path.join(runs_dir, process_img_f_lst[0].split('/')[-4], process_img_f_lst[0].split('/')[-3], 'processed_with_mask')
        # if os.path.exists(output_dir):
        #     print(f'Already had bounding box on {patient_name}')
        #     continue
        os.makedirs(output_dir, exist_ok=True)
        bbox_ls_pat = []
        for idx, process_img_f in enumerate(process_img_f_lst):
            img = cv2.imread(process_img_f, cv2.IMREAD_GRAYSCALE)
            img_height, img_width = img.shape
            # lst_all_img_f.append(process_img_f)
            # lst_all_src_f.append(slide_src_f_lst[idx])

            _, binarized_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            masks = find_connected_components(binarized_img, min_area=30)
            if len(masks) == 0:
                print(f"No valid connected components on {process_img_f}")
                continue
            bbox_ls = []            
            if idx not in duplicated_idx:
                # only have one issue, get bounding box directly
                tissue_mask = sum(masks)
                tissue_bounding_box = bounding_box(tissue_mask)
                bbox_ls.append(tissue_bounding_box)
                print(f"{patient_name}-0{idx+1} only has one tissue with bounding box {tissue_bounding_box}")
            else:
                # have two tissues
                # Find pairs based on shape similarity
                pairs = find_pairs(masks, min_area=50)
                try:
                    mask_group_1, mask_group_2 = merge_pair_masks(masks, pairs)
                    mask_1 = sum([masks[i] for i in mask_group_1])
                    mask_2 = sum([masks[i] for i in mask_group_2])
                    bbox_1, bbox_2 = bounding_box(mask_1), bounding_box(mask_2)
                    bbox_ls.extend([bbox_1, bbox_2])
                    print(f"{patient_name}-0{idx+1} has two tissues with bounding box {bbox_1} and {bbox_2}")
                except:
                    tissue_mask = sum(masks)
                    tissue_bounding_box = bounding_box(tissue_mask)
                    bbox_ls.append(tissue_bounding_box)
                    print(f"{patient_name}-0{idx+1} only has one tissue with bounding box {tissue_bounding_box}")

            # lst_bbox_all.append(bbox_ls)
            fig, ax = plt.subplots(1)
            ax.imshow(binarized_img, cmap='gray')

            for bbox in bbox_ls:
                x, y, w, h = bbox
                rect = patches.Rectangle((x * img_width, y * img_height), w*img_width, h*img_height, linewidth=1, edgecolor='r', facecolor='none')
                ax.add_patch(rect)

            plt.savefig(os.path.join(output_dir, os.path.basename(process_img_f)))
            bbox_ls_pat.append(bbox_ls)

        dict_info = {'source': slide_src_f_lst, 'processed': process_img_f_lst, 'bbox': bbox_ls_pat}
        with open(os.path.join('/share/ymz/valisProject/data/mIF_20_converted_cropped/configs', f"{patient_name}.json"), 'w') as f:
            json.dump(dict_info, f, indent=4)
        # df = DataFrame({'process_image': lst_all_img_f, 'source_image': lst_all_src_f, 'bounding_box': lst_bbox_all})
        # df.to_excel('/home/yuanmingze/tmp/bbox_mIF_175.xlsx', index=False)



            


