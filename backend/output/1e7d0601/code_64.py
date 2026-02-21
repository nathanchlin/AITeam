# 资源打包示例
import zipfile
import os

def create_resource_pack(output_path, resource_dir):
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(resource_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, resource_dir)
                zipf.write(file_path, arcname)

# 资源解包示例
def extract_resource_pack(pack_path, output_dir):
    with zipfile.ZipFile(pack_path, 'r') as zipf:
        zipf.extractall(output_dir)