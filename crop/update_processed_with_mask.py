from json import load
import os
from sys import argv
from matplotlib import patches
import matplotlib.pyplot as plt
import cv2

# cfg_dir = '/share/ymz/valisProject/data/mIF_20_converted_cropped/configs'
cfg_dir = '/home/yuanmingze/data/mIF_175_converted_cropped/configs'
patient_name = argv[1]

cfg = load(open(os.path.join(cfg_dir, patient_name + '.json'), 'r'))
source_lst, processed_lst, bbox_all_lst = cfg['source'], cfg['processed'], cfg['bbox']

for processed, bbox_all in zip(processed_lst, bbox_all_lst):
    os.makedirs(os.path.dirname(processed.replace('processed', 'processed_with_mask_new')), exist_ok=True)
    img = cv2.imread(processed, cv2.IMREAD_GRAYSCALE)
    fig, ax = plt.subplots(1)
    ax.imshow(img, cmap='gray')
    img_height, img_width = img.shape

    for bbox in bbox_all:
        x, y, w, h = bbox
        rect = patches.Rectangle((x * img_width, y * img_height), w*img_width, h*img_height, linewidth=1, edgecolor='r', facecolor='none')
        ax.add_patch(rect)

    plt.savefig(processed.replace('processed', 'processed_with_mask_new'))