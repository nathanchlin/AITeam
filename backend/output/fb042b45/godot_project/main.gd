extends Node2D

var velocity = 0
var gravity = -10
var jump_speed = 20
var is_on_ground = true
var touch_position = Vector2()
var obstacles = []
var jump_sound = null

func _ready():
    # Set the view port to the desired screen dimensions
    $MainScene.viewport_rect = Rect2(0, 0, 720, 1280)
    
    # Load the jump sound
    jump_sound = load("res://jump.wav")

func _process(delta):
    # Handle player input for touch
    for touch in Input.get_touches():
        if touch.is_pressed():
            touch_position = touch.position
            if is_on_ground:
                # Play jump sound
                if jump_sound:
                    jump_sound.play()
                velocity = jump_speed
                is_on_ground = false
        elif touch.is_released():
            # Reset touch position to prevent false jump
            touch_position = Vector2()

    # Update velocity based on gravity
    velocity += gravity * delta
    position.y += velocity * delta

    # Check if player is on the ground
    if position.y < 0:
        position.y = 0
        velocity = 0
        is_on_ground = true

    # Check for collisions with obstacles
    for obstacle in obstacles:
        if _check_collision_with_obstacle(obstacle):
            position.y = obstacle.position.y + obstacle.get_size().y
            velocity = 0
            is_on_ground = true

    # Draw obstacles
    for obstacle in obstacles:
        draw_rect(obstacle.position - obstacle.get_size() / 2, obstacle.get_size(), Color(255, 0, 0, 255))

func _check_collision_with_obstacle(obstacle):
    # Check if the player's position is below the obstacle
    return position.y + 10 > obstacle.position.y

func _draw():
    # Clear the screen with a solid color
    draw_rect(Rect2(0, 0, 720, 1280), Color(255, 255, 255, 255))

    # Draw the player's position
    draw_circle(position, 10, Color(0, 0, 255, 255))

    # Draw the ground line
    draw_line(Vector2(0, 0), Vector2(720, 0), Color(0, 255, 0, 255))

    # Draw the touch position for debugging
    if touch_position != Vector2():
        draw_circle(touch_position, 5, Color(255, 0, 0, 255))