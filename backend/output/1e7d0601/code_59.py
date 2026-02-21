# 示例：使用PIL进行图像压缩
from PIL import Image

def optimize_image(input_path, output_path, max_size=(512, 512), quality=85):
    with Image.open(input_path) as img:
        # 调整大小
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        # 保存优化后的图像
        if img.mode == 'RGBA':
            img.save(output_path, format='PNG', optimize=True)
        else:
            img.save(output_path, format='JPEG', quality=quality, optimize=True)