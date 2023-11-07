from valis import slide_io

# slide_src_f = "/home/yuanmingze/data/mIF_175/P1/Image_222476-P1-01.vsi"
slide_src_f = '/home/yuanmingze/data/mIF_P1_demo/_Image_222476-P1-01_/stack1/01.ets'
slide_src_f = '/home/yuanmingze/data/mIF_P1_demo/_Image_222476-P1-01_/stack10000/frame_t.ets'
# slide_src_f = '/home/yuanmingze/data/mIF_P1_demo_ets/P1_01.ets'
series = 0

# Get reader for slide format
reader_cls = slide_io.get_slide_reader(slide_src_f, series=series) #Get appropriate slide reader class
reader = reader_cls(slide_src_f, series=series) # Instantiate reader

#Get size of images in each pyramid level (width, height)
pyramid_level_sizes_wh = reader.metadata.slide_dimensions
print(pyramid_level_sizes_wh)
slide_io.kill_jvm()