from valis import slide_io
from typing import Union
import cv2
import numpy as np
from sklearn.cluster import KMeans
from scipy.spatial import distance
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import matplotlib.pyplot as plt
import math
from glob import glob

def convert_ets_to_ometiff(slide_src_f: str, converted_slide_f: str, xywh: Union[list, tuple], series: int, level: int):
    assert len(xywh) == 4
    reader_cls = slide_io.get_slide_reader(slide_src_f, series=series)  # Get appropriate slide reader class
    reader = reader_cls(slide_src_f, series=series)  # Instantiate reader

    # Get size of images in each pyramid level (width, height)
    pyramid_level_sizes_wh = reader.metadata.slide_dimensions[level]
    print(f"Original size on level {level}:", pyramid_level_sizes_wh)
    img_width, img_height = pyramid_level_sizes_wh
    x, y, w, h = xywh
    xywh = (int(x*img_width), int(y*img_height), int(w*img_width), int(h*img_height))
    print(f"Output bounding box (xywh): {xywh}")

    slide_io.convert_to_ome_tiff(slide_src_f, converted_slide_f, xywh=xywh, level=level)
    slide_io.kill_jvm()

def calculate_area(masks):
    """
    Calculate the area of each mask.
    
    Parameters:
    - masks: Binary masks of connected components.
    
    Returns:
    - areas: List of areas of each mask.
    """
    return [np.sum(mask) / 255 for mask in masks]

def get_foreground_original_area(slide_src_f: str, processed_img_f: str):
    img = cv2.imread(processed_img_f, cv2.IMREAD_GRAYSCALE)
    _, binarized_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    foreground_propotion = (np.sum(binarized_img) / 255) / (img.shape[0] * img.shape[1])
    reader_cls = slide_io.get_slide_reader(slide_src_f)
    reader = reader_cls(slide_src_f)
    pyramid_level_sizes_wh = reader.metadata.slide_dimensions[0]
    original_area_size = pyramid_level_sizes_wh[0] * pyramid_level_sizes_wh[1] * foreground_propotion
    return original_area_size

def find_connected_components(binary_image, min_area=20):
    """
    Find connected components in a binary image.
    
    Parameters:
    - binary_image: A binary image where connected components are to be found.

    Returns:
    - masks: A list of binary masks, each representing one connected component.
    """
    num_labels, labels_im = cv2.connectedComponents(binary_image)
    masks = []

    for label in range(1, num_labels):
        mask = np.zeros_like(binary_image, dtype=np.uint8)
        mask[labels_im == label] = 255
        if np.sum(mask / 255) >= min_area: 
            masks.append(mask)
            
    return masks

def calculate_shape_features(masks):
    """
    Calculate shape features for clustering.
    Here using Hu Moments as an example.
    """
    shape_features = []
    for mask in masks:
        # Compute Hu Moments
         # Find contours
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Usually, the largest contour is the object of interest
        contour = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(contour)
        # shape_features.append(area)
        # Perimeter
        perimeter = cv2.arcLength(contour, closed=True)

        # # Solidity
        # hull = cv2.convexHull(contour)
        # hull_area = cv2.contourArea(hull)

        
        moments = cv2.moments(mask)
        hu_moments = cv2.HuMoments(moments).flatten()
        # print(area, perimeter, hu_moments)
        shape_features.append([area, perimeter, *hu_moments])
        # shape_features.append(hu_moments)
    
    scaler = MinMaxScaler()
    shape_features = np.array(shape_features)
    # print(shape_features.shape)
    scaled_features = scaler.fit_transform(shape_features)
    return scaled_features

def find_pairs(masks, min_area=500):
    """
    Find pairs of masks that are similar based on shape features and have sufficient area.
    
    Parameters:
    - masks: Binary masks of connected components.
    - min_area: Minimum area to consider a mask.
    
    Returns:
    - pairs: List of index pairs indicating the masks that belong together.
    """
    shape_features = calculate_shape_features(masks)
    print(shape_features)
    areas = calculate_area(masks)
    
    # Filter and sort indices based on area
    mask_indices = [i for i, area in enumerate(areas) if area >= min_area]
    mask_indices.sort(key=lambda x: areas[x], reverse=True)
    
    # Calculate distance matrix
    num_masks = len(masks)
    dist_matrix = np.zeros((num_masks, num_masks))
    for i in range(num_masks):
        for j in range(i+1, num_masks):
            dist_matrix[i, j] = distance.euclidean(shape_features[i], shape_features[j])
            dist_matrix[j, i] = dist_matrix[i, j]
    
    pairs = []
    
    # Iteratively find the closest pair
    while mask_indices:
        i = mask_indices[0]
        if len(mask_indices) == 1:
            # pairs.append([i])
            break
        
        # Find the closest item
        min_dist = np.inf
        min_index = -1
        for j in mask_indices[1:]:
            if dist_matrix[i, j] < min_dist:
                min_dist = dist_matrix[i, j]
                min_index = j
        
        print(i, min_index, min_dist)
        if min_dist > 2:
            break
        # Add pair and remove indices
        pairs.append((i, min_index))
        mask_indices.remove(i)
        mask_indices.remove(min_index)
    
    return pairs

def calculate_center(mask):
    # print(mask.shape)
    y, x = np.where(mask)
    return np.mean(x), np.mean(y)

def calculate_direction(point_a, point_b):
    vector = (point_b[0]-point_a[0], point_b[1]-point_a[1])
    angle = math.degrees(math.atan2(vector[1], vector[0]))
    return vector, angle

def merge_pair_masks(masks: Union[list, tuple], pairs: Union[list, tuple]):
    center_1 = calculate_center(masks[pairs[0][0]])
    center_2 = calculate_center(masks[pairs[0][1]])
    base_vector, base_angle = calculate_direction(center_1, center_2)
    corrected_pairs = [pairs[0]]

    for pair in pairs[1:]:
        center_1 = calculate_center(masks[pair[0]])
        center_2 = calculate_center(masks[pair[1]])
        
        vector, angle = calculate_direction(center_1, center_2)
        if abs(angle - base_angle) < 60:
            if distance.euclidean(vector, base_vector) < 200:
                corrected_pairs.append(pair)
        elif abs(angle - base_angle) > 120:
            if distance.euclidean(calculate_direction(center_2, center_1)[0], base_vector) < 200:
                corrected_pairs.append(pair[::-1])
        else:
            continue

    mask_group_1 = [pair[0] for pair in corrected_pairs]
    mask_group_2 = [pair[1] for pair in corrected_pairs]

    return mask_group_1, mask_group_2

def bounding_box(mask, margin=20):
    # 找到mask中的轮廓
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # 找到边界框
    x, y, w, h = cv2.boundingRect(contours[0])
    for cnt in contours[1:]:
        x1, y1, w1, h1 = cv2.boundingRect(cnt)
        x, y, w, h = min(x, x1), min(y, y1), max(x+w, x1+w1) - min(x, x1), max(y+h, y1+h1) - min(y, y1)
    
    # 添加边缘
    x = max(0, x - margin)
    y = max(0, y - margin)
    w = min(mask.shape[1] - x, w + 2 * margin)
    h = min(mask.shape[0] - y, h + 2 * margin)
    
    # 限制在[0, 1]范围内
    img_height, img_width = mask.shape
    x, w = x / img_width, w / img_width
    y, h = y / img_height, h / img_height
    
    return x, y, w, h