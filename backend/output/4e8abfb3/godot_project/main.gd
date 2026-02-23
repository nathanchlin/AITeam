# path/to/file.gd

extends Node2D

# 游戏主类
var player: Node
var ground: Node
var obstacles: Array<Node>
var score: int
var jumpSpeed: int = 200
var gravity: int = 300
var isJumping: bool = false
var touchPosition: Vector2

func _ready():
    # 初始化游戏场景
    player = Node.new()
    player.name = "Player"
    player.position = Vector2(100, 600)
    add_child(player)

    ground = Node.new()
    ground.name = "Ground"
    ground.position = Vector2(0, 640)
    add_child(ground)

    obstacles = []
    score = 0

    # 设置屏幕尺寸
    get_tree().set_window_size(720, 1280)

    # 创建第一个障碍物
    create_obstacle()

func _process(delta):
    # 处理触摸输入
    if Input.is_action_pressed("ui_select"):
        if not isJumping:
            isJumping = true
            player.position = Vector2(player.position.x, player.position.y - 50)

    # 应用重力
    if not isJumping:
        player.position = Vector2(player.position.x, player.position.y + gravity * delta)
        if player.position.y > 600:
            player.position = Vector2(player.position.x, 600)
            isJumping = false

    # 碰撞检测
    for obstacle in obstacles:
        if is_colliding_with_player(player, obstacle):
            # 碰撞处理逻辑，例如结束游戏或减分
            player.position = Vector2(player.position.x, 600)
            isJumping = false
            break

    # 更新障碍物
    update_obstacles(delta)

    # 计分逻辑
    score += 1
    draw_string(10, 10, "Score: " + str(score))

func _draw():
    # 绘制玩家
    draw_circle(player.position, 25, Color(1, 0, 0, 1))

    # 绘制地面
    draw_rect(ground.position, Vector2(720, 40), Color(0, 1, 0, 1))

    # 绘制障碍物
    for obstacle in obstacles:
        draw_rect(obstacle.position, Vector2(50, 50), Color(1, 1, 0, 1))

func create_obstacle():
    # 创建障碍物
    var obstacle = Node.new()
    obstacle.name = "Obstacle"
    obstacle.position = Vector2(700, random(400, 650))
    add_child(obstacle)
    obstacles.append(obstacle)

func update_obstacles(delta):
    # 更新障碍物位置
    for i, obstacle in enumerate(obstacles):
        obstacle.position = Vector2(obstacle.position.x - 10 * delta, obstacle.position.y)
        # 如果障碍物移出屏幕，则移除它
        if obstacle.position.x < -50:
            remove_child(obstacle)
            obstacles.remove(i)

func is_colliding_with_player(player, obstacle):
    # 检测玩家和障碍物是否碰撞
    var player_half_width = 25 / 2
    var player_half_height = 25 / 2
    var obstacle_half_width = 50 / 2
    var obstacle_half_height = 50 / 2

    return (player.position.x < obstacle.position.x + obstacle_half_width and
            player.position.x + player_half_width > obstacle.position.x and
            player.position.y < obstacle.position.y + obstacle_half_height and
            player.position.y + player_half_height > obstacle.position.y)