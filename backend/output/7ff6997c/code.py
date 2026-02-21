# 创建忍者精灵图的函数
def create_ninja_spritesheet():
    # 使用PIL库创建精灵图
    from PIL import Image, ImageDraw
    
    # 设置每个帧的大小和精灵图尺寸
    frame_width = 64
    frame_height = 64
    columns = 4
    rows = 5
    sheet_width = frame_width * columns
    sheet_height = frame_height * rows
    
    # 创建空白精灵图
    sheet = Image.new('RGBA', (sheet_width, sheet_height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(sheet)
    
    # 绘制跑酷动画帧 (16帧)
    running_frames = []
    for i in range(16):
        row = i // columns
        col = i % columns
        x = col * frame_width
        y = row * frame_height
        
        # 绘制忍者身体 (简化为矩形和圆形组合)
        body_color = (0, 150, 0, 255)  # 绿色身体
        
        # 身体 (矩形)
        draw.rectangle([x+20, y+20, x+44, y+40], fill=body_color)
        
        # 头部 (圆形)
        head_offset = 5 if i % 2 == 0 else 8  # 跑步时的头部上下移动
        draw.ellipse([x+24, y+10+head_offset, x+36, y+22+head_offset], fill=body_color)
        
        # 眼睛
        eye_color = (255, 255, 255, 255)
        draw.ellipse([x+28, y+14+head_offset, x+30, y+16+head_offset], fill=eye_color)
        draw.ellipse([x+32, y+14+head_offset, x+34, y+16+head_offset], fill=eye_color)
        
        # 手臂动画
        arm_angle = math.sin(i * math.pi / 4) * 20
        draw.line([x+20, y+25, x+15+arm_angle, y+30], fill=body_color, width=3)
        draw.line([x+44, y+25, x+49-arm_angle, y+30], fill=body_color, width=3)
        
        # 腿部动画
        leg_offset = 5 if i % 2 == 0 else -5
        draw.line([x+26, y+40, x+24+leg_offset, y+55], fill=body_color, width=3)
        draw.line([x+38, y+40, x+40-leg_offset, y+55], fill=body_color, width=3)
        
        running_frames.append((x, y, frame_width, frame_height))
    
    # 绘制跳跃动画帧 (3帧)
    jump_frames = []
    for i in range(3):
        row = 2
        col = i
        x = col * frame_width
        y = row * frame_height
        
        # 绘制跳跃中的忍者
        body_color = (0, 150, 0, 255)
        
        # 身体
        draw.rectangle([x+20, y+15, x+44, y+35], fill=body_color)
        
        # 头部
        draw.ellipse([x+24, y+5, x+36, y+17], fill=body_color)
        
        # 眼睛
        eye_color = (255, 255, 255, 255)
        draw.ellipse([x+28, y+9, x+30, y+11], fill=eye_color)
        draw.ellipse([x+32, y+9, x+34, y+11], fill=eye_color)
        
        # 手臂 (向上举起)
        draw.line([x+20, y+20, x+15, y+10], fill=body_color, width=3)
        draw.line([x+44, y+20, x+49, y+10], fill=body_color, width=3)
        
        # 腿 (弯曲)
        draw.line([x+26, y+35, x+24, y+50], fill=body_color, width=3)
        draw.line([x+38, y+35, x+40, y+50], fill=body_color, width=3)
        
        jump_frames.append((x, y, frame_width, frame_height))
    
    # 绘制攻击动画帧 (5帧)
    attack_frames = []
    for i in range(5):
        row = 3
        col = i
        x = col * frame_width
        y = row * frame_height
        
        # 绘制攻击中的忍者
        body_color = (0, 150, 0, 255)
        
        # 身体
        draw.rectangle([x+20, y+20, x+44, y+40], fill=body_color)
        
        # 头部
        draw.ellipse([x+24, y+10, x+36, y+22], fill=body_color)
        
        # 眼睛
        eye_color = (255, 255, 255, 255)
        draw.ellipse([x+28, y+14, x+30, y+16], fill=eye_color)
        draw.ellipse([x+32, y+14, x+34, y+16], fill=eye_color)
        
        # 手臂 (持剑攻击)
        sword_x = x + 44 + i * 3
        draw.line([x+44, y+25, sword_x, y+20], fill=body_color, width=3)
        draw.line([sword_x-5, y+15, sword_x+5, y+25], fill=(192, 192, 192, 255), width=2)  # 剑
        
        # 另一只手臂
        draw.line([x+20, y+25, x+15, y+30], fill=body_color, width=3)
        
        # 腿
        draw.line([x+26, y+40, x+24, y+55], fill=body_color, width=3)
        draw.line([x+38, y+40, x+40, y+55], fill=body_color, width=3)
        
        attack_frames.append((x, y, frame_width, frame_height))
    
    # 绘制滑铲动画帧 (2帧)
    slide_frames = []
    for i in range(2):
        row = 4
        col = i
        x = col * frame_width
        y = row * frame_height
        
        # 绘制滑铲中的忍者
        body_color = (0, 150, 0, 255)
        
        # 身体 (水平拉伸)
        draw.rectangle([x+15, y+30, x+49, y+40], fill=body_color)
        
        # 头部
        draw.ellipse([x+20, y+20, x+32, y+30], fill=body_color)
        
        # 眼睛
        eye_color = (255, 255, 255, 255)
        draw.ellipse([x+24, y+24, x+26, y+26], fill=eye_color)
        draw.ellipse([x+28, y+24, x+30, y:26], fill=eye_color)
        
        # 手臂 (前伸)
        draw.line([x+15, y+35, x+10, y+35], fill=body_color, width=3)
        draw.line([x+49, y+35, x+54, y+35], fill=body_color, width=3)
        
        # 腿 (弯曲)
        draw.line([x+24, y+40, x+22, y+55], fill=body_color, width=3)
        draw.line([x+40, y+40, x+42, y+55], fill=body_color, width=3)
        
        slide_frames.append((x, y, frame_width, frame_height))
    
    # 保存精灵图
    sheet.save("ninja_spritesheet.png")
    
    return {
        "running": running_frames,
        "jumping": jump_frames,
        "attacking": attack_frames,
        "sliding": slide_frames
    }