import os
from shutil import copytree
from multiprocessing import Pool

lst_fname = ['P3', 'P6', 'P7', 'P8', 'P9', 'P11', 'P12', 'P13', 'P14', 'P15', 'P17', 'P19', 'P20', 'P21', 'P22', 'P23', 'P25', 'P27', 'P28', 'P29', 'P30', 'P31', 'P32', 'P34', 'P35', 'P36', 'P37', 'P39', 'P40', 'P43', 'P44', 'P45', 'P46', 'P47', 'P49', 'P50', 'P52', 'P53', 'P54', 'P55', 'P56', 'P58', 'P59', 'P61', 'P62', 'P63', 'P64', 'P65', 'P66', 'P67', 'P68', 'P69', 'P70', 'P71', 'P72', 'P73', 'P74', 'P75', 'P76', 'P77', 'P78', 'P79', 'P80', 'P81', 'P82', 'P84', 'P85', 'P87', 'P88', 'P89', 'P90', 'P91', 'P92', 'P93', 'P94', 'P95', 'P96', 'P97', 'P99', 'P101', 'P105', 'P107', 'P108', 'P109', 'P110', 'P111', 'P112', 'P114', 'P115', 'P116', 'P117', 'P118', 'P119', 'P120', 'P121', 'P123', 'P125', 'P126', 'P127', 'P128', 'P129', 'P130', 'P132', 'P133', 'P135', 'P137', 'P138', 'P140', 'P143', 'P146', 'P148', 'P149', 'P150', 'P151', 'P152', 'P154', 'P157', 'P158', 'P159', 'P160', 'P161', 'P163', 'P164', 'P166', 'P168', 'P170', 'P171', 'P172', 'P173', 'P175', 'P176', 'P178', 'P181', 'P184', 'P185']
src_dir = '/home/yuanmingze/results/warped_cell_seg_mIF_175'
dst_dir = '/home/yuanmingze/results/warped_cell_seg_cohort1_175_batch1'

def copy_folder(fname: str):
    copytree(os.path.join(src_dir, fname), os.path.join(dst_dir, fname))
    print(f"copied {fname}")

if __name__ == '__main__':
    with Pool(16) as p:
        p.map(copy_folder, lst_fname)

