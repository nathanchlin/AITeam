def is_in_viewport(object, camera):
    # 将对象位置转换为相机裁剪空间坐标
    position = camera.world_to_screen(object.position)
    
    # 检查是否在相机视锥内
    return (-1 <= position.x <= 1 and 
            -1 <= position.y <= 1 and 
            0 <= position.z <= 1)