import numpy as np
import tifffile

with tifffile.TiffFile('/public/share/ymz/valisProject/data/mIF_175_converted_cropped/images/P71/P71-03-1.ome.tiff') as tif:
    image = tif.asarray()
    ome_metadata = tif.ome_metadata  # 获取OME元数据

flipped_image = image[:, ::-1, :]

tifffile.imwrite(
    '/public/share/ymz/valisProject/data/mIF_175_converted_cropped/images/P71/P71-03-2.ome.tiff',
    flipped_image,
    metadata={'ome': ome_metadata},  # 写入OME元数据
    compression='lzw'  # 使用zlib压缩，也可尝试其他如'lzw'
)

# import pyvips

# # 加载OME-TIFF图像
# image = pyvips.Image.new_from_file('/public/share/ymz/valisProject/data/mIF_175_converted_cropped/images/P71/P71-03-1.ome.tiff')
# print('Number of channels:', image.bands)

# # 沿x轴镜像翻转图像
# flipped_image = image.fliphor()
# print('Number of channels:', flipped_image.bands)

# # 保存翻转后的图像
# flipped_image.write_to_file('/public/share/ymz/valisProject/data/mIF_175_converted_cropped/images/P71/P71-03-2.ome.tiff')
