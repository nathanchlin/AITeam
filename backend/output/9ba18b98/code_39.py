def clear_lines_animation(screen, board, lines_to_clear, x, y):
    """消行动画效果"""
    for line in lines_to_clear:
        # 绘制闪烁效果
        for i in range(3):
            # 白色闪烁
            for j in range(len(board[line])):
                rect = pygame.Rect(
                    x + j * BLOCK_SIZE,
                    y + line * BLOCK_SIZE,
                    BLOCK_SIZE,
                    BLOCK_SIZE
                )
                pygame.draw.rect(screen, (255, 255, 255), rect)
            pygame.display.flip()
            pygame.time.wait(100)
            
            # 恢复原色
            draw_board(screen, board, x, y)
            pygame.display.flip()
            pygame.time.wait(100)
    
    # 消除行
    for line in sorted(lines_to_clear, reverse=True):
        del board[line]
        board.insert(0, [0 for _ in range(len(board[0]))])