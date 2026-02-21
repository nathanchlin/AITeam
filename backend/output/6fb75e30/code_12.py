class GameController:
    def __init__(self):
        self.state_manager = GameStateManager()
        self.character = Character()
        self.character_controller = CharacterController(self.character)
        self.obstacle_generator = ObstacleGenerator()
        self.collision_detector = CollisionDetector()
        self.collision_handler = CollisionHandler(self.character, ScoreManager())
        self.score_manager = ScoreManager()
        self.game_speed = INITIAL_GAME_SPEED
        
        # 注册事件监听
        EventSystem.on("game_over", self._on_game_over)
        EventSystem.on("state_changed", self._on_state_changed)
    
    def update(self, delta_time):
        """更新游戏逻辑"""
        if self.state_manager.current_state == GameState.PLAYING:
            # 更新游戏速度
            self.game_speed = min(MAX_GAME_SPEED, INITIAL_GAME_SPEED + self.score_manager.current_score / 100)
            
            # 更新各系统
            self.character_controller.update(delta_time)
            self.obstacle_generator.update(delta_time, self.game_speed)
            
            # 更新碰撞检测
            obstacles = self.obstacle_generator.get_active_obstacles()
            self.collision_detector.update(self.character, obstacles)
            collisions = self.collision_detector.check_collisions()
            self.collision_handler.handle_collisions(collisions, obstacles)
            self.collision_handler.check_score(obstacles)
            
            # 清理非活动障碍物
            self.obstacle_generator.remove_inactive_obstacles()
    
    def _on_game_over(self, data):
        """游戏结束处理"""
        self.state_manager.change_state(GameState.GAME_OVER)
        self.score_manager.save_high_score()
    
    def _on_state_changed(self, data):
        """状态变更处理"""
        if data["to"] == GameState.PLAYING:
            # 重置游戏状态
            self.character = Character()
            self.character_controller = CharacterController(self.character)
            self.obstacle_generator = ObstacleGenerator()
            self.collision_detector = CollisionDetector()
            self.collision_handler = CollisionHandler(self.character, self.score_manager)
            self.game_speed = INITIAL_GAME_SPEED
        elif data["to"] == GameState.MENU:
            # 返回菜单
            pass