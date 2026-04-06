"""动画生成工具 - 为 Animator Agent 提供动画代码生成能力

支持生成 CSS 动画、GSAP 动画、游戏动画参数
"""

from typing import Optional, Dict, Any


# 预定义动画模板
ANIMATION_TEMPLATES = {
    # 基础动画
    "bounce": {
        "description": "弹跳效果，适合按钮、图标强调",
        "keyframes": """
@keyframes bounce {{
  0%, 100% {{ transform: translateY(0); }}
  25% {{ transform: translateY(-{amplitude}px); }}
  50% {{ transform: translateY(-{amplitude_h}px); }}
  75% {{ transform: translateY(-{amplitude_q}px); }}
}}
""",
        "defaults": {"amplitude": 20, "amplitude_h": 10, "amplitude_q": 5}
    },
    "pulse": {
        "description": "脉冲效果，适合吸引用户注意",
        "keyframes": """
@keyframes pulse {{
  0% {{ transform: scale(1); opacity: 1; }}
  50% {{ transform: scale({scale}); opacity: {opacity}; }}
  100% {{ transform: scale(1); opacity: 1; }}
}}
""",
        "defaults": {"scale": 1.1, "opacity": 0.8}
    },
    "shake": {
        "description": "抖动效果，适合错误提示、警告",
        "keyframes": """
@keyframes shake {{
  0%, 100% {{ transform: translateX(0); }}
  10%, 30%, 50%, 70%, 90% {{ transform: translateX(-{amplitude}px); }}
  20%, 40%, 60%, 80% {{ transform: translateX({amplitude}px); }}
}}
""",
        "defaults": {"amplitude": 5}
    },
    "fadeIn": {
        "description": "淡入效果",
        "keyframes": """
@keyframes fadeIn {{
  from {{ opacity: 0; }}
  to {{ opacity: 1; }}
}}
"""
    },
    "fadeOut": {
        "description": "淡出效果",
        "keyframes": """
@keyframes fadeOut {{
  from {{ opacity: 1; }}
  to {{ opacity: 0; }}
}}
"""
    },
    "slideInLeft": {
        "description": "从左侧滑入",
        "keyframes": """
@keyframes slideInLeft {{
  from {{ transform: translateX(-100%); opacity: 0; }}
  to {{ transform: translateX(0); opacity: 1; }}
}}
"""
    },
    "slideInRight": {
        "description": "从右侧滑入",
        "keyframes": """
@keyframes slideInRight {{
  from {{ transform: translateX(100%); opacity: 0; }}
  to {{ transform: translateX(0); opacity: 1; }}
}}
"""
    },
    "slideInUp": {
        "description": "从下方滑入",
        "keyframes": """
@keyframes slideInUp {{
  from {{ transform: translateY(100%); opacity: 0; }}
  to {{ transform: translateY(0); opacity: 1; }}
}}
"""
    },
    "rotate": {
        "description": "旋转效果",
        "keyframes": """
@keyframes rotate {{
  from {{ transform: rotate(0deg); }}
  to {{ transform: rotate({degrees}deg); }}
}}
""",
        "defaults": {"degrees": 360}
    },
    "swing": {
        "description": "摇摆效果，适合悬停交互",
        "keyframes": """
@keyframes swing {{
  20% {{ transform: rotate({angle}deg); }}
  40% {{ transform: rotate(-{angle_h}deg); }}
  60% {{ transform: rotate({angle_q}deg); }}
  80% {{ transform: rotate(-{angle_e}deg); }}
  100% {{ transform: rotate(0deg); }}
}}
""",
        "defaults": {"angle": 15, "angle_h": 10, "angle_q": 5, "angle_e": 3}
    },
    "heartbeat": {
        "description": "心跳效果，适合点赞、收藏",
        "keyframes": """
@keyframes heartbeat {{
  0% {{ transform: scale(1); }}
  14% {{ transform: scale({scale}); }}
  28% {{ transform: scale(1); }}
  42% {{ transform: scale({scale}); }}
  70% {{ transform: scale(1); }}
}}
""",
        "defaults": {"scale": 1.3}
    },
    "float": {
        "description": "悬浮效果，适合游戏角色、装饰元素",
        "keyframes": """
@keyframes float {{
  0%, 100% {{ transform: translateY(0); }}
  50% {{ transform: translateY(-{amplitude}px); }}
}}
""",
        "defaults": {"amplitude": 10}
    },
    "glow": {
        "description": "发光效果，适合强调、高亮",
        "keyframes": """
@keyframes glow {{
  0%, 100% {{ 
    box-shadow: 0 0 {size}px {color}, 0 0 {size2}px {color}; 
  }}
  50% {{ 
    box-shadow: 0 0 {size3}px {color}, 0 0 {size4}px {color}, 0 0 {size5}px {color}; 
  }}
}}
""",
        "defaults": {"size": 5, "size2": 10, "size3": 10, "size4": 20, "size5": 30, "color": "#4facfe"}
    },
    "wiggle": {
        "description": "扭动效果，适合可爱元素、游戏角色",
        "keyframes": """
@keyframes wiggle {{
  0%, 100% {{ transform: rotate(0deg); }}
  25% {{ transform: rotate({angle}deg); }}
  75% {{ transform: rotate(-{angle}deg); }}
}}
""",
        "defaults": {"angle": 3}
    },
}

# 缓动函数
EASING_FUNCTIONS = {
    "linear": "linear",
    "ease": "ease",
    "ease-in": "ease-in",
    "ease-out": "ease-out",
    "ease-in-out": "ease-in-out",
    "bounce": "cubic-bezier(0.68, -0.55, 0.265, 1.55)",
    "elastic": "cubic-bezier(0.68, -0.6, 0.32, 1.6)",
    "smooth": "cubic-bezier(0.4, 0, 0.2, 1)",
    "sharp": "cubic-bezier(0.4, 0, 0.6, 1)",
}


async def generate_css_animation(
    animation_type: str,
    duration: float = 1.0,
    easing: str = "ease-in-out",
    iteration: str = "infinite",
    delay: float = 0.0,
    custom_params: Optional[Dict[str, Any]] = None,
    _sandbox: Optional[Dict[str, Any]] = None
) -> str:
    """生成 CSS 动画代码
    
    Args:
        animation_type: 动画类型
            - bounce: 弹跳
            - pulse: 脉冲
            - shake: 抖动
            - fadeIn/fadeOut: 淡入/淡出
            - slideInLeft/slideInRight/slideInUp: 滑入
            - rotate: 旋转
            - swing: 摇摆
            - heartbeat: 心跳
            - float: 悬浮（游戏常用）
            - glow: 发光
            - wiggle: 扭动
        
        duration: 动画持续时间（秒），默认 1.0
        
        easing: 缓动函数
            - linear, ease, ease-in, ease-out, ease-in-out
            - bounce: 弹性
            - elastic: 橡皮筋
            - smooth: 平滑
            - sharp: 锐利
        
        iteration: 动画次数
            - "infinite": 无限循环（默认）
            - "1", "2", "3"...: 指定次数
        
        delay: 动画延迟时间（秒），默认 0.0
        
        custom_params: 自定义参数（可选）
            - bounce: amplitude (默认 20)
            - pulse: scale (默认 1.1), opacity (默认 0.8)
            - shake: amplitude (默认 5)
            - rotate: degrees (默认 360)
            - float: amplitude (默认 10)
            - glow: color (默认 #4facfe)
    
    Returns:
        完整的 CSS 动画代码，包括 @keyframes 和使用示例
    """
    # 检查动画类型是否存在
    if animation_type not in ANIMATION_TEMPLATES:
        available = list(ANIMATION_TEMPLATES.keys())
        return f"""❌ 未知的动画类型: {animation_type}

可用的动画类型:
{chr(10).join(f'  - {k}: {ANIMATION_TEMPLATES[k]["description"]}' for k in available[:10])}
  
请选择上述类型之一。"""

    template = ANIMATION_TEMPLATES[animation_type]
    
    # 合并默认参数和自定义参数
    params = template.get("defaults", {}).copy()
    if custom_params:
        params.update(custom_params)
    
    # 格式化关键帧
    keyframes = template["keyframes"].format(**params)
    
    # 获取缓动函数
    easing_func = EASING_FUNCTIONS.get(easing, easing)
    
    # 生成完整的 CSS 代码
    css_code = f"""/* {template['description']} */
{keyframes}

/* 使用示例 */
.animated-element {{
  animation: {animation_type} {duration}s {easing_func} {iteration};
  animation-delay: {delay}s;
}}

/* 悬停时暂停 */
.animated-element:hover {{
  animation-play-state: paused;
}}

/* 兼容性前缀 */
.animated-element {{
  -webkit-animation: {animation_type} {duration}s {easing_func} {iteration};
  -moz-animation: {animation_type} {duration}s {easing_func} {iteration};
  -o-animation: {animation_type} {duration}s {easing_func} {iteration};
}}
"""

    return css_code


async def generate_game_animation(
    character_type: str,
    action: str,
    style: str = "cartoon",
    frame_count: int = 8,
    _sandbox: Optional[Dict[str, Any]] = None
) -> str:
    """生成游戏角色动画参数
    
    Args:
        character_type: 角色类型
            - player: 玩家角色
            - enemy: 敌人
            - npc: NPC
            - boss: Boss
            - projectile: 子弹/投射物
        
        action: 动作类型
            - idle: 待机
            - walk: 行走
            - run: 奔跑
            - jump: 跳跃
            - attack: 攻击
            - hurt: 受伤
            - death: 死亡
            - fly: 飞行
        
        style: 动画风格
            - cartoon: 卡通（默认）
            - realistic: 写实
            - pixel-art: 像素风
            - anime: 动漫风
        
        frame_count: 帧数，默认 8
    
    Returns:
        JavaScript/Canvas 动画参数和实现建议
    """
    
    # 预定义的动画参数
    animation_presets = {
        "player": {
            "idle": {
                "frames": 4,
                "duration": 1.0,
                "loop": True,
                "description": "轻微呼吸/悬浮效果",
                "params": {"offsetY": 2, "scale": 0.02}
            },
            "walk": {
                "frames": 8,
                "duration": 0.6,
                "loop": True,
                "description": "腿部交替运动",
                "params": {"legAngle": 15, "bodyBob": 3}
            },
            "run": {
                "frames": 6,
                "duration": 0.4,
                "loop": True,
                "description": "快速奔跑",
                "params": {"legAngle": 30, "bodyBob": 5, "armSwing": 20}
            },
            "jump": {
                "frames": 6,
                "duration": 0.8,
                "loop": False,
                "description": "跳跃弧线",
                "params": {"jumpHeight": 50, "squat": 0.8, "stretch": 1.2}
            },
            "attack": {
                "frames": 4,
                "duration": 0.3,
                "loop": False,
                "description": "攻击动作",
                "params": {"windup": -15, "strike": 30, "followThrough": 10}
            },
            "hurt": {
                "frames": 3,
                "duration": 0.3,
                "loop": False,
                "description": "受伤闪烁",
                "params": {"flash": True, "shake": 5}
            },
            "death": {
                "frames": 8,
                "duration": 1.0,
                "loop": False,
                "description": "倒下动画",
                "params": {"rotation": 90, "fade": True}
            },
        },
        "enemy": {
            "idle": {
                "frames": 4,
                "duration": 1.2,
                "loop": True,
                "description": "威胁性悬浮",
                "params": {"offsetY": 3, "rotation": 2}
            },
            "attack": {
                "frames": 5,
                "duration": 0.5,
                "loop": False,
                "description": "扑向玩家",
                "params": {"scale": 1.2, "moveY": 20}
            },
        },
        "projectile": {
            "fly": {
                "frames": 2,
                "duration": 0.2,
                "loop": True,
                "description": "子弹旋转",
                "params": {"rotation": 360}
            },
        }
    }
    
    # 获取动画参数
    char_animations = animation_presets.get(character_type, animation_presets["player"])
    anim_params = char_animations.get(action)
    
    if not anim_params:
        # 生成通用参数
        anim_params = {
            "frames": frame_count,
            "duration": 0.5,
            "loop": True,
            "description": f"自定义 {action} 动画",
            "params": {}
        }
    
    # 生成 JavaScript 代码
    js_code = f"""/**
 * 游戏动画参数生成
 * 角色: {character_type}
 * 动作: {action}
 * 风格: {style}
 */

const animation = {{
  name: '{character_type}_{action}',
  frames: {anim_params['frames']},
  frameDuration: {anim_params['duration'] / anim_params['frames']:.3f},
  totalDuration: {anim_params['duration']},
  loop: {str(anim_params['loop']).lower()},
  
  // 动画参数
  params: {anim_params['params']},
  
  // 缓动函数
  easing: (t) => {{
    // ease-in-out
    return t < 0.5 
      ? 2 * t * t 
      : 1 - Math.pow(-2 * t + 2, 2) / 2;
  }},
  
  // 获取当前帧的变换
  getTransform: function(frameIndex) {{
    const progress = frameIndex / this.frames;
    const p = this.params;
    
    // 基于 {style} 风格的变换计算
    switch ('{action}') {{
      case 'idle':
        return {{
          offsetY: Math.sin(progress * Math.PI * 2) * (p.offsetY || 2),
          scale: 1 + Math.sin(progress * Math.PI * 2) * (p.scale || 0.02)
        }};
      
      case 'jump':
        const jumpProgress = this.easing(progress);
        return {{
          offsetY: -Math.sin(jumpProgress * Math.PI) * (p.jumpHeight || 50),
          scaleY: progress < 0.3 ? (p.squat || 0.8) : 
                  progress > 0.7 ? (p.stretch || 1.2) : 1
        }};
      
      case 'attack':
        const attackAngle = progress < 0.4 
          ? (p.windup || -15)
          : progress < 0.7 
            ? (p.strike || 30)
            : (p.followThrough || 10);
        return {{ rotation: attackAngle }};
      
      case 'hurt':
        return {{
          opacity: progress % 0.2 < 0.1 ? 0.3 : 1,
          offsetX: Math.sin(progress * Math.PI * 20) * (p.shake || 5)
        }};
      
      default:
        return {{}};
    }}
  }}
}};

// Canvas 绘制示例
function drawAnimatedCharacter(ctx, x, y, frameIndex) {{
  const transform = animation.getTransform(frameIndex);
  
  ctx.save();
  ctx.translate(x, y + (transform.offsetY || 0));
  
  if (transform.scale) {{
    ctx.scale(1 + transform.scale, 1 + transform.scale);
  }}
  if (transform.scaleY) {{
    ctx.scale(1, transform.scaleY);
  }}
  if (transform.rotation) {{
    ctx.rotate(transform.rotation * Math.PI / 180);
  }}
  if (transform.opacity !== undefined) {{
    ctx.globalAlpha = transform.opacity;
  }}
  
  // 绘制角色
  drawCharacter(ctx, 0, 0);
  
  ctx.restore();
}}
"""

    return js_code


async def list_available_animations(
    _sandbox: Optional[Dict[str, Any]] = None
) -> str:
    """列出所有可用的动画类型和参数
    
    Returns:
        动画类型列表和使用说明
    """
    css_animations = "\n".join([
        f"- **{name}**: {info['description']}"
        for name, info in ANIMATION_TEMPLATES.items()
    ])
    
    easings = "\n".join([
        f"- `{name}`: {desc if name not in EASING_FUNCTIONS else EASING_FUNCTIONS.get(name, name)}"
        for name, desc in [
            ("linear", "线性"),
            ("ease", "默认缓动"),
            ("ease-in", "加速"),
            ("ease-out", "减速"),
            ("ease-in-out", "先加后减"),
            ("bounce", "弹性"),
            ("elastic", "橡皮筋"),
            ("smooth", "平滑"),
        ]
    ])
    
    return f"""# 🎨 可用动画类型

## CSS 动画

{css_animations}

## 缓动函数

{easings}

## 使用示例

### 1. 基础用法
```
generate_css_animation(
  animation_type="bounce",
  duration=0.5,
  easing="bounce"
)
```

### 2. 自定义参数
```
generate_css_animation(
  animation_type="bounce",
  duration=1.0,
  custom_params={{"amplitude": 30}}
)
```

### 3. 游戏动画
```
generate_game_animation(
  character_type="player",
  action="jump",
  style="cartoon"
)
```

## 最佳实践

1. **UI 交互**: 使用 `pulse`, `bounce`, `shake`
2. **页面过渡**: 使用 `fadeIn`, `slideInLeft`, `slideInRight`
3. **游戏角色**: 使用 `float`, `wiggle`, `rotate`
4. **强调元素**: 使用 `glow`, `heartbeat`
"""


# 工具元数据
ANIMATION_TOOLS = [
    {
        "name": "generate_css_animation",
        "description": "生成 CSS 动画代码。支持弹跳、脉冲、抖动、淡入淡出、滑入、旋转、心跳、悬浮等 15+ 种动画。返回完整的 CSS 代码，可直接使用。",
        "parameters": {
            "type": "object",
            "properties": {
                "animation_type": {
                    "type": "string",
                    "enum": list(ANIMATION_TEMPLATES.keys()),
                    "description": "动画类型：bounce(弹跳), pulse(脉冲), shake(抖动), fadeIn/fadeOut(淡入淡出), slideIn*(滑入), rotate(旋转), swing(摇摆), heartbeat(心跳), float(悬浮), glow(发光), wiggle(扭动)"
                },
                "duration": {
                    "type": "number",
                    "default": 1.0,
                    "description": "动画持续时间（秒）"
                },
                "easing": {
                    "type": "string",
                    "default": "ease-in-out",
                    "description": "缓动函数：linear, ease, ease-in, ease-out, ease-in-out, bounce, elastic, smooth"
                },
                "iteration": {
                    "type": "string",
                    "default": "infinite",
                    "description": "动画次数：infinite(无限) 或数字"
                },
                "delay": {
                    "type": "number",
                    "default": 0.0,
                    "description": "动画延迟时间（秒）"
                },
                "custom_params": {
                    "type": "object",
                    "description": "自定义参数，如 bounce 的 amplitude, pulse 的 scale"
                }
            },
            "required": ["animation_type"]
        },
        "handler": generate_css_animation,
    },
    {
        "name": "generate_game_animation",
        "description": "生成游戏角色动画参数。为 Canvas/Web 游戏生成角色动画的 JavaScript 参数和代码示例。",
        "parameters": {
            "type": "object",
            "properties": {
                "character_type": {
                    "type": "string",
                    "enum": ["player", "enemy", "npc", "boss", "projectile"],
                    "default": "player",
                    "description": "角色类型"
                },
                "action": {
                    "type": "string",
                    "enum": ["idle", "walk", "run", "jump", "attack", "hurt", "death", "fly"],
                    "default": "idle",
                    "description": "动作类型"
                },
                "style": {
                    "type": "string",
                    "enum": ["cartoon", "realistic", "pixel-art", "anime"],
                    "default": "cartoon",
                    "description": "动画风格"
                },
                "frame_count": {
                    "type": "integer",
                    "default": 8,
                    "description": "帧数"
                }
            },
            "required": ["character_type", "action"]
        },
        "handler": generate_game_animation,
    },
    {
        "name": "list_available_animations",
        "description": "列出所有可用的动画类型、参数和使用示例。",
        "parameters": {
            "type": "object",
            "properties": {}
        },
        "handler": list_available_animations,
    },
]
