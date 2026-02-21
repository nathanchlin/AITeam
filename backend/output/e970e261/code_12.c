int main() {
    Mario mario;
    init_mario(&mario, 100, 300);
    
    bool left_pressed = false;
    bool right_pressed = false;
    bool up_pressed = false;
    bool down_pressed = false;
    bool action_pressed = false;
    
    while (game_running) {
        // 获取输入
        get_input(&left_pressed, &right_pressed, &up_pressed, &down_pressed, &action_pressed);
        
        // 处理输入和更新状态
        handle_input(&mario, left_pressed, right_pressed, up_pressed, down_pressed, action_pressed);
        update_mario(&mario);
        
        // 渲染
        clear_screen();
        render_mario(&mario);
        present_screen();
        
        // 控制帧率
        delay(16); // 约60FPS
    }
    
    return 0;
}