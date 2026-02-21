def optimized_collision_detection(game_objects):
    """优化的碰撞检测流程"""
    # 1. 按层分组
    groups = CollisionGroups()
    for obj in game_objects:
        groups.add_object(obj, obj.group)
    
    # 2. 只检测可能碰撞的组
    collision_pairs = []
    
    # 玩家与陨石
    collision_pairs.extend(groups.get_potential_collisions("player", "asteroid"))
    
    # 玩家子弹与敌人
    collision_pairs.extend(groups.get_potential_collisions("bullet", "enemy"))
    
    # 3. 使用四叉树优化每组内的碰撞检测
    quadtree = QuadTree(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
    
    for pair in collision_pairs:
        obj1, obj2 = pair
        # 先进行粗略检测
        if aabb_collision(obj1.boundary, obj2.boundary):
            # 再进行精确检测
            if precise_collision(obj1, obj2):
                yield (obj1, obj2)  # 返回碰撞对