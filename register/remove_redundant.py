import os
from shutil import rmtree
from tqdm import tqdm

src_dir = '/public/share/ymz/valisProject/results'
lst_fname = os.listdir(src_dir)
for fname in tqdm(lst_fname):
    if os.listdir(os.path.join(src_dir, fname)) == ['registered_slides']:
        rmtree(os.path.join(src_dir, fname))


