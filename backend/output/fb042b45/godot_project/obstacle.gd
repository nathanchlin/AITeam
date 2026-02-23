extends Node2D

var size = Vector2(50, 10)

func _ready():
    # Draw the obstacle using draw_rect
    draw_rect(Rect2(-size.x / 2, -size.y / 2, size.x, size.y), Color(255, 0, 0, 255))