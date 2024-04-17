from valis import slide_io
from json import load
from sys import argv
import os

# cfg_dir = '/share/ymz/valisProject/data/mIF_175_converted_cropped/configs'
cfg_dir = '/home/yuanmingze/data/mIF_175_converted_cropped/configs'
# output_dir = '/share/ymz/valisProject/data/mIF_20_converted_cropped/images_tmp'
output_dir = '/home/yuanmingze/data/mIF_175_converted_cropped/images'
patient_name = argv[1]
print(patient_name)
cfg = load(open(os.path.join(cfg_dir, patient_name + '.json'), 'r'))

source_lst, processed_lst, bbox_all_lst = cfg['source'], cfg['processed'], cfg['bbox']
# slide_src_f = "/home/yuanmingze/data/mIF_P1_demo/_Image_222476-P1-01_/stack1/frame_t.ets"
# slide_src_f = '/share/ymz/valisProject/data/mIF_175_organized/P19/_Image_223010-P19-03_/stack1/frame_t.ets'
# converted_slide_f = "/home/yuanmingze/tmp/P19_03_2.ome.tiff"
series = 2
level = 2
os.makedirs(os.path.join(output_dir, patient_name), exist_ok=True)

for source, processed, bbox_all in zip(source_lst, processed_lst, bbox_all_lst):
    # Get reader for slide format
    reader_cls = slide_io.get_slide_reader(source, series=series) #Get appropriate slide reader class
    reader = reader_cls(source, series=series) # Instantiate reader

    #Get size of images in each pyramid level (width, height)
    pyramid_level_sizes_wh = reader.metadata.slide_dimensions[level]
    print(pyramid_level_sizes_wh)
    img_width, img_height = pyramid_level_sizes_wh
    # x, y, w, h = (0.08333333333333333, 0.27147766323024053, 0.32175925925925924, 0.6254295532646048)
    # x, y, w, h = (0.6944444444444444, 0.3745704467353952, 0.3055555555555556, 0.6254295532646048)
    fname = os.path.basename(processed).removesuffix('.png')
    for idx, bbox in enumerate(bbox_all):
        x, y, w, h = bbox
        xywh = (int(x*img_width), int(y*img_height), int(w*img_width), int(h*img_height))
        print(xywh)
        converted_slide_f = os.path.join(output_dir, patient_name, f"{fname}-{idx+1}.ome.tiff")
        slide_io.convert_to_ome_tiff(source,
                                    converted_slide_f,
                                    xywh=xywh,
                                    level=level)
    
    
slide_io.kill_jvm()