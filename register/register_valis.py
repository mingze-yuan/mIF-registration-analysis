from valis import registration
import os
from datetime import datetime

formatted_date = datetime.now().strftime('%Y-%m-%d-%H%M%S')
# slide_src_dir = "/home/yuanmingze/data/mIF_P1_demo"
# slide_src_dir = '/share/ymz/valisProject/data/mIF_175_organized/P70'
slide_src_dir = '/home/yuanmingze/data/mIF_20_organized/01009'
results_dst_dir = os.path.join("/home/yuanmingze/results_modified_20", os.path.basename(slide_src_dir) + f'_{formatted_date}')
# registered_slide_dst_dir = os.path.join(results_dst_dir, 'registered_slides')
# results_dst_dir = "/home/yuanmingze/results/mIF_P1_demo_new"
# registered_slide_dst_dir = "/home/yuanmingze/results/mIF_P1_demo_s2/registered_slides"
registered_slide_dst_dir = os.path.join(results_dst_dir, 'registered_slides')


# Create a Valis object and use it to register the slides in slide_src_dir
registrar = registration.Valis(slide_src_dir, results_dst_dir, imgs_ordered=True, thumbnail_size=2048)
rigid_registrar, non_rigid_registrar, error_df = registrar.register()

# Perform micro-registration on higher resolution images, aligning *directly to* the reference image
registrar.register_micro(max_non_rigid_registration_dim_px=3000, align_to_reference=True)
# Save all registered slides as ome.tiff
registrar.warp_and_save_slides(registered_slide_dst_dir, crop="overlap", level=2)

# Kill the JVM
registration.kill_jvm()