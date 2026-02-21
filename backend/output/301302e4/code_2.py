class GameLevelLoader:
    @staticmethod
    def load_level(filename):
        """从文件加载关卡用于游戏"""
        with open(filename, 'r') as f:
            level_data = json.load(f)
        
        obstacles = []
        for obs_data in level_data["obstacles"]:
            # 转换字符串类型的枚举值为实际枚举
            obs_data["type"] = ObstacleType(obs_data["type"])
            obstacles.append(Obstacle(**obs_data))
        
        return obstacles
    
    @staticmethod
    def create_physics_bodies(obstacles, physics_world):
        """为障碍物创建物理体"""
        bodies = []
        for obstacle in obstacles:
            if obstacle.type == ObstacleType.BLOCK:
                # 创建矩形物理体
                body = physics_world.create_box(
                    position=(obstacle.x, obstacle.y),
                    size=(obstacle.width, obstacle.height),
                    mass=5.0,
                    friction=0.5
                )
            elif obstacle.type == ObstacleType.CIRCLE:
                # 创建圆形物理体
                body = physics_world.create_circle(
                    position=(obstacle.x + obstacle.width/2, obstacle.y + obstacle.height/2),
                    radius=obstacle.width/2,
                    mass=3.0,
                    friction=0.3
                )
            elif obstacle.type == ObstacleType.TRIANGLE:
                # 创建多边形物理体
                body = physics_world.create_polygon(
                    vertices=[
                        (obstacle.x + obstacle.width/2, obstacle.y),
                        (obstacle.x, obstacle.y + obstacle.height),
                        (obstacle.x + obstacle.width, obstacle.y + obstacle.height)
                    ],
                    mass=4.0,
                    friction=0.4
                )
            elif obstacle.type == ObstacleType.PLATFORM:
                # 创建静态平台
                body = physics_world.create_box(
                    position=(obstacle.x, obstacle.y),
                    size=(obstacle.width, obstacle.height),
                    mass=0.0,  # 静态物体
                    friction=0.7
                )
            elif obstacle.type == ObstacleType.PIG:
                # 创建猪（可破坏）
                body = physics_world.create_circle(
                    position=(obstacle.x + obstacle.width/2, obstacle.y + obstacle.height/2),
                    radius=obstacle.width/2,
                    mass=1.0,
                    friction=0.2,
                    destructible=True,
                    health=obstacle.properties.get("health", 100)
                )
            
            if body:
                body.obstacle_type = obstacle.type
                bodies.append(body)
        
        return bodies