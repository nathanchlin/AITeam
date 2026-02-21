def add_jump_effect(particle_system, ninja_pos):
    # 跳跃时向上喷射的粒子
    particle_system.emit(
        ninja_pos[0], ninja_pos[1],
        count=15,
        color=(0, 255, 100),  # 亮绿色
        min_velocity=(0, -100),
        max_velocity=(0, -50),
        min_size=3,
        max_size=6,
        lifetime=0.3
    )