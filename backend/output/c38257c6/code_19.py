def handle_mouse_motion(self, event):
       """处理鼠标移动事件"""
       if event.type == pygame.MOUSEMOTION:
           paddle_rect.centerx = event.pos[0]