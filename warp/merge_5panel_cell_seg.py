import os
import pandas as pd
from glob import glob
from multiprocessing import Pool

# cell_seg_dir = '/public/share/ymz/valisProject/data/cell_annotation_175/data_175'
# cell_seg_dir = '/share/pbao/SPEC-lightning/data_175_converted_1106_x_y'
# cell_seg_dir = '/home/yuanmingze/data/update_10'
# cell_seg_dir = '/share/pbao/SPEC/data_175_new'
# warped_coord_pth = '/home/yuanmingze/results/warped_coordinate_mIF_175/P1/Image_222476-P1-01.vsi - 20x_01_cells_warped.csv'
# ori_cell_seg_pth = '/public/share/ymz/valisProject/data/cell_annotation_175/data_175/P1/cell seg data/Image_222476-P1-01.vsi - 20x_01_cells.tsv'
# warped_coord_dir = '/home/yuanmingze/results/warped_coordinate_mIF_175'
# warped_coord_dir = '/home/yuanmingze/data/update_10'
# dst_dir = '/home/yuanmingze/results/warped_cell_seg_mIF_175_Mar1_debug'


cell_seg_dir = '/home/yuanmingze/data/PBN202200225FW/cell seg data'
warped_coord_dir = '/home/yuanmingze/results/warped_coordinate_mIF_20'
dst_dir = '/home/yuanmingze/results/warped_cell_seg_mIF_20'

def remove_specific_columns(df: pd.DataFrame, substrings: list[str]):
    cols_to_drop = [col for col in df.columns for sub in substrings if sub in col]
    df.drop(columns=cols_to_drop, inplace=True)
    return df

def find_associated_ori_cell_seg_from_warped_coord_pth(warped_coord_pth: str):
    filename = os.path.basename(warped_coord_pth)
    if filename.startswith('Image_'):
        # ori_cell_seg_found_lst = glob(os.path.join(cell_seg_dir, '*', 'cell seg data', filename.replace('_warped.csv', '.tsv')))
        ori_cell_seg_found_lst = glob(os.path.join(cell_seg_dir, '*', 'Cell seg data', filename.replace('_warped.csv', '.tsv')))
        
        assert len(ori_cell_seg_found_lst) == 1
        return ori_cell_seg_found_lst[0]
    elif filename.startswith('P'):
        pattern_to_search = '-'.join(filename.split('-')[:2])
        print(pattern_to_search)
        ori_cell_seg_found_lst = glob(os.path.join(cell_seg_dir, '*', 'Cell seg data', f"*{pattern_to_search}*_cells.tsv"))
        # ori_cell_seg_found_lst = glob(os.path.join(cell_seg_dir, 'cell seg data', '*', f"*{pattern_to_search}*_cells.tsv"))
        # print(ori_cell_seg_found_lst)

        assert len(ori_cell_seg_found_lst) == 1
        return ori_cell_seg_found_lst[0]
    else:
        raise ValueError(f"Unknown warped coordinates filenames for {warped_coord_pth}")
        
def merge_warped_coord_and_ori_cell_seg(warped_coord_pth: str, ori_cell_seg_pth: str, panel_id: int = 0):
    warped_coord = pd.read_csv(warped_coord_pth)
    print(f"Load warped coordinates with {len(warped_coord)} rows")
    # print(warped_coord.columns)
    ori_cell_seg = pd.read_csv(ori_cell_seg_pth, delimiter='\t')
    ori_cell_seg = remove_specific_columns(ori_cell_seg, ['min', 'std', 'sum', 'range'])
    print(f"Load cell segmentation data with {len(ori_cell_seg)} rows")
    # print(ori_cell_seg.columns)
    columns_to_drop = ['Centroid X px', 'Centroid Y px', 'Warped Centroid X px', 'Warped Centroid Y px']
    warped_coord = warped_coord.drop(columns=columns_to_drop, errors='ignore')
    # print(ori_cell_seg.head())
    # print(warped_coord.columns, ori_cell_seg.columns)
    merged_df = pd.merge(warped_coord, ori_cell_seg, on=['Centroid X µm', 'Centroid Y µm'], how='inner')
    print(f"The merged table has {len(merged_df)} rows")

    if panel_id:
        merged_df['panel_id'] = panel_id
        column_order = ['panel_id'] + [col for col in merged_df.columns if col != 'panel_id']
        merged_df = merged_df[column_order]    
    return merged_df, len(warped_coord), len(ori_cell_seg)

def get_file_index(filename: str):
    # Image_222495-P2-02.vsi - 20x_01_cells_warped.csv -> P2-02
    # P3-01-1_warped -> P3-01
    print(filename)
    if filename.startswith('Image_'):
        file_index = '-'.join(filename.split('.vsi')[0].split('-')[1:3])
    elif filename.startswith('P'):
        # file_index = '-'.join(filename.split('-')[:2])
        file_index = filename.split('_')[0]
    return file_index

def get_panel_id(ori_cell_seg_pth: str):
    # input: */data_175/P4/cell seg data/Image_222573-P1-04.vsi - 20x_01_cells.tsv
    # output: 4
    print(ori_cell_seg_pth)
    # print(ori_cell_seg_pth)
    return int(ori_cell_seg_pth.split('/')[-3][1])

def process_one_folder(folder: str):
    # try:
    if os.path.exists(os.path.join(dst_dir, folder)) and len(os.listdir(os.path.join(dst_dir, folder))) == 7:
        print(f'already finished {folder}')
        return
    info_summary = {'index': [], 'num_ori_cell_seg': [], 'num_warped_coord': [], 'num_final': []}
    folder_pth = os.path.join(warped_coord_dir, folder)
    # if len(os.listdir(folder_pth)) != 5:
    #     print(f"The number of files in {folder} is not 5")
    #     return
    lst_filename = sorted(os.listdir(folder_pth), key=get_file_index)
    dst_folder_pth = os.path.join(dst_dir, folder)
    os.makedirs(dst_folder_pth, exist_ok=True)

    merged_df_lst = []
    for idx, filename in enumerate(lst_filename):
        print(f"-------- [{idx+1}/{len(os.listdir(folder_pth))}] {filename} --------")
        warped_coord_pth = os.path.join(folder_pth, filename)
        ori_cell_seg_pth = find_associated_ori_cell_seg_from_warped_coord_pth(warped_coord_pth)
        panel_id = get_panel_id(ori_cell_seg_pth)
        file_index = get_file_index(filename)

        merged_df, num_warped_coord, num_ori_cell_seg = merge_warped_coord_and_ori_cell_seg(
            warped_coord_pth=warped_coord_pth,
            ori_cell_seg_pth=ori_cell_seg_pth,
            panel_id=panel_id)
        
        merged_df.to_csv(os.path.join(dst_folder_pth, f'{file_index}.csv'), index=False)
        merged_df_lst.append(merged_df)
        info_summary['index'].append(file_index)
        info_summary['num_ori_cell_seg'].append(num_ori_cell_seg)
        info_summary['num_warped_coord'].append(num_warped_coord)
        info_summary['num_final'].append(len(merged_df))
    
    merged_df_stacked = pd.concat(merged_df_lst, axis=0, ignore_index=True, sort=False)
    # print(merged_df_stacked.columns)
    merged_df_stacked.to_csv(os.path.join(dst_folder_pth, f'{folder}_stacked.csv'), index=False)
    df_info_summary = pd.DataFrame(info_summary)
    df_info_summary.to_excel(os.path.join(dst_folder_pth, 'num_summary.xlsx'), index=False)
    # except:
    #     return folder
        
if __name__ == "__main__":
    lst_folder = sorted(os.listdir(warped_coord_dir))
    # lst_folder = [x for x in lst_folder if x not in ['P1', 'P10', 'P100', 'P124', 'P142', 'P144', 'P147', 'P165', 'P177', 'P2', 'P5', 'P98', 'P16', 'P189', 'P103']]
    # lst_folder = ['P1', 'P10', 'P100', 'P124', 'P142', 'P144', 'P147', 'P165', 'P177', 'P2', 'P5', 'P98']
    # lst_folder = ['P98']
    # lst_folder = ['P1', 'P2', "P142", 'P98', 'P100', 'P124', 'P144', 'P147', 'P165', 'P177']
    # lst_folder = ['P103', 'P189']


    # lst_folder = ['P83', 'P86']
    # merged_df = merge_warped_coord_and_ori_cell_seg(warped_coord_pth, ori_cell_seg_pth, panel_id=1)
    # print(merged_df.columns, merged_df.head())
    # process_one_folder(lst_folder[0])
    # folder = 'P3'
    # process_one_folder(folder)
    with Pool(16) as p:
        fail_cases = p.map(process_one_folder, lst_folder)
    # lst_folder = ['P1']
    print(fail_cases)
    # print([x for x in fail_cases if x is not None])
    # for folder in lst_folder:
    #     print(folder)
    #     process_one_folder(folder)

