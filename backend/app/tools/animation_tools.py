"""动画生成工具 - 为 Animator Agent 提供动画代码生成能力

支持生成 CSS 动画、GSAP 动画、游戏动画参数、Lottie JSON、Godot 动画
"""

import json
from typing import Optional, Dict, Any, List


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

### 4. 交互动画
```
generate_animation(
  description="按钮悬停时放大并改变背景色",
  trigger="hover",
  framework="css"
)
```

## 最佳实践

1. **UI 交互**: 使用 `pulse`, `bounce`, `shake`
2. **页面过渡**: 使用 `fadeIn`, `slideInLeft`, `slideInRight`
3. **游戏角色**: 使用 `float`, `wiggle`, `rotate`
4. **强调元素**: 使用 `glow`, `heartbeat`
"""


async def generate_animation(
    description: str,
    trigger: str = "auto",
    framework: str = "css",
    duration: float = 0.5,
    easing: str = "ease-in-out",
    _sandbox: Optional[Dict[str, Any]] = None
) -> str:
    """根据自然语言描述生成动画代码
    
    Args:
        description: 动画描述（自然语言）
            示例："按钮悬停时放大并旋转"
            "弹窗从底部滑入"
            "图标左右摇晃"
        
        trigger: 触发方式
            - "auto": 自动播放（默认）
            - "hover": 鼠标悬停
            - "click": 点击
            - "scroll": 滚动触发
            - "load": 页面加载
        
        framework: 输出框架
            - "css": 纯 CSS（默认）
            - "gsap": GSAP JavaScript 库
            "animejs": Anime.js 库
        
        duration: 动画持续时间（秒），默认 0.5
        
        easing: 缓动函数，默认 "ease-in-out"
    
    Returns:
        完整的动画代码（CSS/JS）
    """
    
    description_lower = description.lower()
    
    # 基于描述智能选择动画类型
    animation_type = "pulse"  # 默认
    custom_params = {}
    
    # 匹配关键词
    if any(kw in description_lower for kw in ["弹跳", "bounce", "跳"]):
        animation_type = "bounce"
    elif any(kw in description_lower for kw in ["悬停", "漂浮", "悬浮", "float", "hover"]):
        animation_type = "float"
    elif any(kw in description_lower for kw in ["摇摆", "摇晃", "shake", "wiggle"]):
        animation_type = "wiggle" if "扭" in description_lower else "shake"
    elif any(kw in description_lower for kw in ["淡入", "fadein", "出现"]):
        animation_type = "fadeIn"
    elif any(kw in description_lower for kw in ["淡出", "fadeout", "消失"]):
        animation_type = "fadeOut"
    elif any(kw in description_lower for kw in ["滑入", "slide"]):
        if "左" in description_lower:
            animation_type = "slideInLeft"
        elif "右" in description_lower:
            animation_type = "slideInRight"
        else:
            animation_type = "slideInUp"
    elif any(kw in description_lower for kw in ["旋转", "rotate", "转"]):
        animation_type = "rotate"
        custom_params = {"degrees": 360}
    elif any(kw in description_lower for kw in ["心跳", "pulse", "脉搏"]):
        animation_type = "heartbeat"
    elif any(kw in description_lower for kw in ["发光", "glow", "闪烁"]):
        animation_type = "glow"
    elif any(kw in description_lower for kw in ["放大", "缩放", "scale"]):
        animation_type = "pulse"
        custom_params = {"scale": 1.2, "opacity": 0.9}
    
    # 根据框架生成代码
    if framework == "css":
        return await _generate_css_with_trigger(
            animation_type, trigger, duration, easing, custom_params
        )
    elif framework == "gsap":
        return await _generate_gsap_animation(
            description, animation_type, trigger, duration, easing
        )
    else:
        return await _generate_css_with_trigger(
            animation_type, trigger, duration, easing, custom_params
        )


async def _generate_css_with_trigger(
    animation_type: str,
    trigger: str,
    duration: float,
    easing: str,
    custom_params: Dict[str, Any]
) -> str:
    """生成带触发器的 CSS 动画"""
    
    # 获取基础动画
    base_animation = await generate_css_animation(
        animation_type=animation_type,
        duration=duration,
        easing=easing,
        iteration="infinite" if trigger == "auto" else "1",
        custom_params=custom_params
    )
    
    # 根据触发器添加额外代码
    trigger_code = ""
    
    if trigger == "hover":
        trigger_code = f"""
/* 悬停触发 */
.trigger-element {{
  /* 默认状态 */
  transition: all {duration}s {easing};
}}

.trigger-element:hover {{
  animation: {animation_type} {duration}s {easing};
}}
"""
    elif trigger == "click":
        trigger_code = f"""
/* 点击触发 - 需要 JavaScript */
<button class="trigger-button" onclick="this.classList.toggle('animated')">
  点击触发动画
</button>

<style>
.trigger-button {{
  /* 默认状态 */
}}

.trigger-button.animated {{
  animation: {animation_type} {duration}s {easing};
}}
</style>
"""
    elif trigger == "scroll":
        trigger_code = f"""
/* 滚动触发 - 需要 JavaScript */
<div class="scroll-animate" data-animation="{animation_type}">
  滚动到此处触发动画
</div>

<script>
// 使用 Intersection Observer
const observer = new IntersectionObserver((entries) => {{
  entries.forEach(entry => {{
    if (entry.isIntersecting) {{
      entry.target.style.animation = `${{entry.target.dataset.animation}} {duration}s {easing}`;
      observer.unobserve(entry.target);
    }}
  }});
}});

document.querySelectorAll('.scroll-animate').forEach(el => observer.observe(el));
</script>
"""
    elif trigger == "load":
        trigger_code = f"""
/* 页面加载触发 */
.load-animate {{
  animation: {animation_type} {duration}s {easing};
  animation-delay: 0.2s;
  animation-fill-mode: both;
}}
"""
    
    return f"{base_animation}\n\n{trigger_code}"


async def _generate_gsap_animation(
    description: str,
    animation_type: str,
    trigger: str,
    duration: float,
    easing: str
) -> str:
    """生成 GSAP 动画代码"""
    
    # GSAP 缓动映射
    gsap_easing = {
        "linear": "none",
        "ease": "power1.out",
        "ease-in": "power1.in",
        "ease-out": "power1.out",
        "ease-in-out": "power1.inOut",
        "bounce": "bounce.out",
        "elastic": "elastic.out(1, 0.3)",
        "smooth": "power2.inOut",
    }
    
    ease = gsap_easing.get(easing, "power1.inOut")
    
    # 根据动画类型生成 GSAP 代码
    gsap_code = f"""// GSAP 动画: {description}
// 需要引入 GSAP: <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>

"""

    if animation_type == "bounce":
        gsap_code += f"""gsap.fromTo(".animated-element", 
  {{ y: 0 }},
  {{
    y: -20,
    duration: {duration / 2},
    ease: "{ease}",
    yoyo: true,
    repeat: -1
  }}
);
"""
    elif animation_type == "float":
        gsap_code += f"""gsap.to(".animated-element", {{
  y: -10,
  duration: {duration},
  ease: "{ease}",
  yoyo: true,
  repeat: -1
}});
"""
    elif animation_type == "fadeIn":
        gsap_code += f"""gsap.from(".animated-element", {{
  opacity: 0,
  duration: {duration},
  ease: "{ease}"
}});
"""
    elif animation_type == "slideInUp":
        gsap_code += f"""gsap.from(".animated-element", {{
  y: 100,
  opacity: 0,
  duration: {duration},
  ease: "{ease}"
}});
"""
    elif animation_type == "rotate":
        gsap_code += f"""gsap.to(".animated-element", {{
  rotation: 360,
  duration: {duration},
  ease: "{ease}",
  repeat: -1
}});
"""
    else:
        gsap_code += f"""// 自定义动画
gsap.to(".animated-element", {{
  duration: {duration},
  ease: "{ease}"
}});
"""

    # 添加触发器代码
    if trigger == "hover":
        gsap_code += f"""
// 悬停触发
const element = document.querySelector(".animated-element");
element.addEventListener("mouseenter", () => {{
  gsap.to(element, {{
    scale: 1.1,
    duration: {duration},
    ease: "{ease}"
  }});
}});
element.addEventListener("mouseleave", () => {{
  gsap.to(element, {{
    scale: 1,
    duration: {duration},
    ease: "{ease}"
  }});
}});
"""
    elif trigger == "scroll":
        gsap_code += f"""
// 滚动触发（需要 ScrollTrigger 插件）
gsap.registerPlugin(ScrollTrigger);

gsap.from(".animated-element", {{
  scrollTrigger: {{
    trigger: ".animated-element",
    start: "top center",
    toggleActions: "play none none reverse"
  }},
  opacity: 0,
  y: 50,
  duration: {duration},
  ease: "{ease}"
}});
"""

    return gsap_code


# 工具元数据


# ==================== Lottie 动画生成 ====================

async def generate_lottie_animation(
    animation_type: str,
    duration: float = 1.0,
    width: int = 100,
    height: int = 100,
    color: str = "#4facfe",
    loop: bool = True,
    custom_params: Optional[Dict[str, Any]] = None,
    _sandbox: Optional[Dict[str, Any]] = None
) -> str:
    """生成 Lottie JSON 动画
    
    Args:
        animation_type: 动画类型
            - move: 位置移动
            - scale: 缩放
            - rotate: 旋转
            - fade: 透明度变化
            - bounce: 弹跳（组合动画）
            - shake: 抖动（组合动画）
        
        duration: 动画持续时间（秒）
        width: 画布宽度
        height: 画布高度
        color: 元素颜色
        loop: 是否循环
        custom_params: 自定义参数
    
    Returns:
        Lottie JSON 格式的动画数据 + 预览 HTML
    """
    
    # 解析颜色
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
    
    rgb = hex_to_rgb(color)
    
    # 帧率
    fps = 60
    total_frames = int(duration * fps)
    
    # 基础 Lottie 结构
    lottie = {
        "v": "5.7.1",
        "fr": fps,
        "ip": 0,
        "op": total_frames,
        "w": width,
        "h": height,
        "nm": f"{animation_type}_animation",
        "ddd": 0,
        "assets": [],
        "layers": []
    }
    
    # 默认参数
    params = custom_params or {}
    
    # 创建形状层
    layer = {
        "ddd": 0,
        "ind": 1,
        "ty": 4,  # 形状层
        "nm": "shape_layer",
        "sr": 1,
        "ks": {
            "o": {"a": 0, "k": 100},  # 透明度
            "r": {"a": 0, "k": 0},     # 旋转
            "p": {"a": 0, "k": [width/2, height/2, 0]},  # 位置
            "a": {"a": 0, "k": [0, 0, 0]},  # 锚点
            "s": {"a": 0, "k": [100, 100, 100]}  # 缩放
        },
        "ao": 0,
        "shapes": [
            {
                "ty": "rc",  # 矩形
                "d": 1,
                "s": {"a": 0, "k": [40, 40]},  # 尺寸
                "p": {"a": 0, "k": [0, 0]},    # 位置
                "r": {"a": 0, "k": 5},         # 圆角
                "nm": "rectangle"
            },
            {
                "ty": "fl",  # 填充
                "c": {"a": 0, "k": rgb},
                "o": {"a": 0, "k": 100},
                "r": 1,
                "nm": "fill"
            }
        ],
        "ip": 0,
        "op": total_frames,
        "st": 0,
        "bm": 0
    }
    
    # 根据动画类型添加关键帧
    if animation_type == "move":
        move_x = params.get("move_x", 30)
        move_y = params.get("move_y", 0)
        
        layer["ks"]["p"] = {
            "a": 1,
            "k": [
                {
                    "t": 0,
                    "s": [width/2 - move_x, height/2 - move_y, 0],
                    "e": [width/2 + move_x, height/2 + move_y, 0],
                    "i": {"x": [0.4], "y": [1]},
                    "o": {"x": [0.6], "y": [0]}
                },
                {"t": total_frames}
            ]
        }
    
    elif animation_type == "scale":
        scale_from = params.get("scale_from", 50)
        scale_to = params.get("scale_to", 150)
        
        layer["ks"]["s"] = {
            "a": 1,
            "k": [
                {
                    "t": 0,
                    "s": [scale_from, scale_from, 100],
                    "e": [scale_to, scale_to, 100],
                    "i": {"x": [0.4], "y": [1]},
                    "o": {"x": [0.6], "y": [0]}
                },
                {"t": total_frames}
            ]
        }
    
    elif animation_type == "rotate":
        degrees = params.get("rotate_degrees", 360)
        
        layer["ks"]["r"] = {
            "a": 1,
            "k": [
                {
                    "t": 0,
                    "s": [0],
                    "e": [degrees],
                    "i": {"x": [0.4], "y": [1]},
                    "o": {"x": [0.6], "y": [0]}
                },
                {"t": total_frames}
            ]
        }
    
    elif animation_type == "fade":
        opacity_from = params.get("opacity_from", 100)
        opacity_to = params.get("opacity_to", 0)
        
        layer["ks"]["o"] = {
            "a": 1,
            "k": [
                {
                    "t": 0,
                    "s": [opacity_from],
                    "e": [opacity_to],
                    "i": {"x": [0.4], "y": [1]},
                    "o": {"x": [0.6], "y": [0]}
                },
                {"t": total_frames}
            ]
        }
    
    elif animation_type == "bounce":
        # 弹跳：缩放 + 位置
        amplitude = params.get("amplitude", 20)
        
        layer["ks"]["p"] = {
            "a": 1,
            "k": [
                {"t": 0, "s": [width/2, height/2, 0], "e": [width/2, height/2 - amplitude, 0]},
                {"t": total_frames // 4, "s": [width/2, height/2 - amplitude, 0], "e": [width/2, height/2, 0]},
                {"t": total_frames // 2, "s": [width/2, height/2, 0], "e": [width/2, height/2 - amplitude/2, 0]},
                {"t": total_frames * 3 // 4, "s": [width/2, height/2 - amplitude/2, 0], "e": [width/2, height/2, 0]},
                {"t": total_frames}
            ]
        }
    
    elif animation_type == "shake":
        # 抖动：旋转 + 位置
        amplitude = params.get("amplitude", 5)
        
        shake_keys = []
        for i in range(0, total_frames, total_frames // 10):
            angle = amplitude if (i // (total_frames // 10)) % 2 == 0 else -amplitude
            shake_keys.append({"t": i, "s": [angle]})
        shake_keys.append({"t": total_frames, "s": [0]})
        
        layer["ks"]["r"] = {"a": 1, "k": shake_keys}
    
    lottie["layers"].append(layer)
    
    # 如果不循环，添加停止
    if not loop:
        lottie["op"] = total_frames
    
    # 生成预览 HTML
    preview_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Lottie Animation Preview</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
</head>
<body style="margin:0; display:flex; justify-content:center; align-items:center; min-height:100vh; background:#1a1a1a;">
    <div id="animation" style="width:{width*2}px; height:{height*2}px;"></div>
    <script>
        const animationData = {json.dumps(lottie)};
        
        const anim = lottie.loadAnimation({{
            container: document.getElementById('animation'),
            renderer: 'svg',
            loop: {str(loop).lower()},
            autoplay: true,
            animationData: animationData
        }});
    </script>
</body>
</html>"""
    
    return json.dumps({
        "lottie_json": lottie,
        "preview_html": preview_html,
        "usage": {
            "web": "使用 lottie-web 库播放",
            "ios": "使用 Lottie iOS 库",
            "android": "使用 Lottie Android 库",
            "react": "使用 react-lottie 库"
        }
    }, indent=2)


# ==================== Godot 动画生成 ====================

async def generate_godot_animation(
    animation_name: str,
    duration: float,
    tracks: List[Dict[str, Any]],
    _sandbox: Optional[Dict[str, Any]] = None
) -> str:
    """生成 Godot 引擎动画资源
    
    Args:
        animation_name: 动画名称
        duration: 动画持续时间
        tracks: 动画轨道列表
            [
                {
                    "property": "position:y",
                    "keys": [[0, 0, 1], [0.5, 100, 0.5], [1.0, 0, 1]]
                    # [time, value, transition]
                }
            ]
    
    Returns:
        Godot .tres 动画资源文件
    """
    
    # 生成 .tres 文件内容
    tres_content = f"""[gd_resource type="Animation" load_steps={len(tracks) + 1} format=3 uid="uid://animation_{animation_name}"]

[resource]
resource_name = "{animation_name}"
length = {duration}
loop_mode = 1
step = 0.01
"""
    
    # 添加轨道
    for i, track in enumerate(tracks):
        prop = track.get("property", "position:y")
        keys = track.get("keys", [])
        
        tres_content += f"""
tracks/{i}/type = "value"
tracks/{i}/imported = false
tracks/{i}/enabled = true
tracks/{i}/path = NodePath("..:{prop}")
tracks/{i}/interp = 1
tracks/{i}/loop_wrap = true
tracks/{i}/keys = {{
"""
        
        # 添加关键帧
        key_count = len(keys)
        tres_content += f"subkeys = {key_count}, " + "\n"
        
        for j, key in enumerate(keys):
            time, value, transition = key if len(key) == 3 else (key[0], key[1], 1.0)
            tres_content += f"{time}, {transition}, {value}"
            if j < key_count - 1:
                tres_content += ", "
        
        tres_content += "\n}\n"
    
    # 生成使用示例
    usage = f"""
# Godot 使用示例
# 1. 将此内容保存为 animation_{animation_name}.tres
# 2. 在场景中添加 AnimationPlayer 节点
# 3. 加载动画资源并播放

extends Node2D

@onready var animation_player = $AnimationPlayer

func _ready():
    var anim = load("res://animation_{animation_name}.tres")
    animation_player.add_animation("{animation_name}", anim)
    animation_player.play("{animation_name}")
"""
    
    return json.dumps({
        "tres_content": tres_content,
        "gdscript_usage": usage,
        "filename": f"animation_{animation_name}.tres"
    }, indent=2)

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
    {
        "name": "generate_lottie_animation",
        "description": "生成 Lottie JSON 动画。支持位置、缩放、旋转、透明度动画，输出可在 Web/iOS/Android 播放的 JSON 文件。",
        "parameters": {
            "type": "object",
            "properties": {
                "animation_type": {
                    "type": "string",
                    "description": "动画类型：move(移动), scale(缩放), rotate(旋转), fade(透明度), bounce(弹跳), shake(抖动)"
                },
                "duration": {
                    "type": "number",
                    "default": 1.0,
                    "description": "动画持续时间（秒）"
                },
                "width": {
                    "type": "integer",
                    "default": 100,
                    "description": "画布宽度（像素）"
                },
                "height": {
                    "type": "integer",
                    "default": 100,
                    "description": "画布高度（像素）"
                },
                "color": {
                    "type": "string",
                    "default": "#4facfe",
                    "description": "动画元素颜色（十六进制）"
                },
                "loop": {
                    "type": "boolean",
                    "default": True,
                    "description": "是否循环播放"
                },
                "custom_params": {
                    "type": "object",
                    "description": "自定义参数：move_x, move_y, scale_from, scale_to, rotate_degrees, opacity_from, opacity_to"
                }
            },
            "required": ["animation_type"]
        },
        "handler": generate_lottie_animation,
    },
    {
        "name": "generate_godot_animation",
        "description": "生成 Godot 引擎动画资源。支持 Godot 4.x 的 AnimationPlayer 格式，输出 .tres 文件。",
        "parameters": {
            "type": "object",
            "properties": {
                "animation_name": {
                    "type": "string",
                    "default": "default",
                    "description": "动画名称"
                },
                "duration": {
                    "type": "number",
                    "default": 1.0,
                    "description": "动画持续时间（秒）"
                },
                "tracks": {
                    "type": "array",
                    "description": "动画轨道列表",
                    "items": {
                        "type": "object",
                        "properties": {
                            "property": {
                                "type": "string",
                                "description": "属性路径，如 'position:y', 'scale', 'rotation_degrees'"
                            },
                            "keys": {
                                "type": "array",
                                "description": "关键帧数组 [[time, value, transition], ...]"
                            }
                        }
                    }
                }
            },
            "required": ["tracks"]
        },
        "handler": generate_godot_animation,
    },
]

# ==================== Lottie 高级功能 ====================

async def generate_lottie_path_animation(
    path_data: str,
    duration: float = 2.0,
    stroke_width: float = 3.0,
    stroke_color: str = "#4facfe",
    fill_color: Optional[str] = None,
    width: int = 400,
    height: int = 400,
    _sandbox: Optional[Dict[str, Any]] = None
) -> str:
    """生成 SVG 路径动画（Lottie 格式）
    
    Args:
        path_data: SVG 路径数据（d 属性）
            示例："M 100,100 L 200,100 L 150,50 Z"
        
        duration: 动画持续时间（秒）
        stroke_width: 描边宽度
        stroke_color: 描边颜色
        fill_color: 填充颜色（可选）
        width: 画布宽度
        height: 画布高度
    
    Returns:
        路径绘制动画的 Lottie JSON
    """
    
    fps = 60
    total_frames = int(duration * fps)
    
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
    
    stroke_rgb = hex_to_rgb(stroke_color)
    fill_rgb = hex_to_rgb(fill_color) if fill_color else [1, 1, 1]
    
    lottie = {
        "v": "5.7.1",
        "fr": fps,
        "ip": 0,
        "op": total_frames,
        "w": width,
        "h": height,
        "nm": "path_animation",
        "ddd": 0,
        "assets": [],
        "layers": [{
            "ddd": 0,
            "ind": 1,
            "ty": 4,
            "nm": "path_layer",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [width/2, height/2, 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "shapes": [
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "sh",
                            "d": 1,
                            "ks": {
                                "a": 0,
                                "k": {
                                    "c": True,
                                    "v": _parse_svg_path(path_data),
                                    "i": [],
                                    "o": []
                                }
                            }
                        },
                        {
                            "ty": "st",
                            "c": {"a": 0, "k": stroke_rgb},
                            "o": {"a": 0, "k": 100},
                            "w": {
                                "a": 1,
                                "k": [
                                    {"t": 0, "s": [0], "e": [stroke_width]},
                                    {"t": total_frames, "s": [stroke_width]}
                                ]
                            },
                            "lc": 2,
                            "lj": 2
                        },
                        {
                            "ty": "tr",
                            "p": {"a": 0, "k": [0, 0]},
                            "a": {"a": 0, "k": [0, 0]},
                            "s": {"a": 0, "k": [100, 100]},
                            "r": {"a": 0, "k": 0},
                            "o": {"a": 0, "k": 100}
                        }
                    ],
                    "nm": "path_group"
                }
            ],
            "ip": 0,
            "op": total_frames,
            "st": 0,
            "bm": 0
        }]
    }
    
    # 如果有填充，添加填充形状
    if fill_color:
        lottie["layers"][0]["shapes"][0]["it"].insert(2, {
            "ty": "fl",
            "c": {"a": 0, "k": fill_rgb},
            "o": {"a": 0, "k": 100},
            "r": 1
        })
    
    preview_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Lottie Path Animation</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
</head>
<body style="margin:0; display:flex; justify-content:center; align-items:center; min-height:100vh; background:#1a1a1a;">
    <div id="animation" style="width:{width*1.5}px; height:{height*1.5}px; border:1px solid #333;"></div>
    <script>
        const anim = lottie.loadAnimation({{
            container: document.getElementById('animation'),
            renderer: 'svg',
            loop: true,
            autoplay: true,
            animationData: {json.dumps(lottie)}
        }});
    </script>
</body>
</html>"""
    
    return json.dumps({
        "lottie_json": lottie,
        "preview_html": preview_html,
        "usage": {
            "description": "SVG 路径绘制动画",
            "svg_path": path_data,
            "duration": f"{duration}秒"
        }
    }, indent=2)


def _parse_svg_path(path_data: str) -> List:
    """解析 SVG 路径数据为 Lottie 顶点格式"""
    # 简化的路径解析
    vertices = []
    commands = path_data.split()
    
    i = 0
    while i < len(commands):
        cmd = commands[i]
        
        if cmd == 'M':  # 移动
            x, y = float(commands[i+1]), float(commands[i+2])
            vertices.append([x - 200, y - 200])  # 居中
            i += 3
        elif cmd == 'L':  # 直线
            x, y = float(commands[i+1]), float(commands[i+2])
            vertices.append([x - 200, y - 200])
            i += 3
        elif cmd == 'Z':  # 闭合
            i += 1
        else:
            i += 1
    
    return vertices


async def generate_lottie_shape_morph(
    start_shape: str,
    end_shape: str,
    duration: float = 1.5,
    width: int = 200,
    height: int = 200,
    color: str = "#4facfe",
    _sandbox: Optional[Dict[str, Any]] = None
) -> str:
    """生成形状变化动画（Shape Morph）
    
    Args:
        start_shape: 起始形状
            - "circle": 圆形
            - "square": 正方形
            - "triangle": 三角形
            - "star": 星形
        
        end_shape: 结束形状（同上）
        duration: 动画持续时间
        width: 画布宽度
        height: 画布高度
        color: 填充颜色
    
    Returns:
        形状变化动画的 Lottie JSON
    """
    
    fps = 60
    total_frames = int(duration * fps)
    
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return [int(hex_color[i:i+2], 16) / 255 for i in (0, 2, 4)]
    
    rgb = hex_to_rgb(color)
    
    # 定义形状顶点
    shapes = {
        "circle": {
            "c": True,
            "v": [[0, -40], [40, 0], [0, 40], [-40, 0]],
            "i": [[0, -22], [22, 0], [0, 22], [-22, 0]],
            "o": [[0, 22], [-22, 0], [0, -22], [22, 0]]
        },
        "square": {
            "c": True,
            "v": [[-35, -35], [35, -35], [35, 35], [-35, 35]],
            "i": [[0, 0], [0, 0], [0, 0], [0, 0]],
            "o": [[0, 0], [0, 0], [0, 0], [0, 0]]
        },
        "triangle": {
            "c": True,
            "v": [[0, -40], [40, 35], [-40, 35]],
            "i": [[0, 0], [0, 0], [0, 0]],
            "o": [[0, 0], [0, 0], [0, 0]]
        },
        "star": {
            "c": True,
            "v": [[0, -45], [12, -15], [45, -15], [20, 8], [28, 40], [0, 22], [-28, 40], [-20, 8], [-45, -15], [-12, -15]],
            "i": [[0, 0]] * 10,
            "o": [[0, 0]] * 10
        }
    }
    
    start = shapes.get(start_shape, shapes["circle"])
    end = shapes.get(end_shape, shapes["square"])
    
    lottie = {
        "v": "5.7.1",
        "fr": fps,
        "ip": 0,
        "op": total_frames,
        "w": width,
        "h": height,
        "nm": f"{start_shape}_to_{end_shape}_morph",
        "ddd": 0,
        "assets": [],
        "layers": [{
            "ddd": 0,
            "ind": 1,
            "ty": 4,
            "nm": "morph_layer",
            "sr": 1,
            "ks": {
                "o": {"a": 0, "k": 100},
                "r": {"a": 0, "k": 0},
                "p": {"a": 0, "k": [width/2, height/2, 0]},
                "a": {"a": 0, "k": [0, 0, 0]},
                "s": {"a": 0, "k": [100, 100, 100]}
            },
            "ao": 0,
            "shapes": [
                {
                    "ty": "gr",
                    "it": [
                        {
                            "ty": "sh",
                            "d": 1,
                            "ks": {
                                "a": 1,
                                "k": [
                                    {
                                        "t": 0,
                                        "s": [start],
                                        "e": [end]
                                    },
                                    {
                                        "t": total_frames,
                                        "s": [end]
                                    }
                                ]
                            }
                        },
                        {
                            "ty": "fl",
                            "c": {"a": 0, "k": rgb},
                            "o": {"a": 0, "k": 100},
                            "r": 1
                        },
                        {
                            "ty": "tr",
                            "p": {"a": 0, "k": [0, 0]},
                            "a": {"a": 0, "k": [0, 0]},
                            "s": {"a": 0, "k": [100, 100]},
                            "r": {"a": 0, "k": 0},
                            "o": {"a": 0, "k": 100}
                        }
                    ],
                    "nm": "morph_group"
                }
            ],
            "ip": 0,
            "op": total_frames,
            "st": 0,
            "bm": 0
        }]
    }
    
    preview_html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Lottie Shape Morph</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/lottie-web/5.12.2/lottie.min.js"></script>
</head>
<body style="margin:0; display:flex; flex-direction:column; align-items:center; justify-content:center; min-height:100vh; background:#1a1a1a;">
    <h2 style="color:#fff; font-family:Arial;">{start_shape.title()} → {end_shape.title()}</h2>
    <div id="animation" style="width:{width*2}px; height:{height*2}px;"></div>
    <script>
        const anim = lottie.loadAnimation({{
            container: document.getElementById('animation'),
            renderer: 'svg',
            loop: true,
            autoplay: true,
            animationData: {json.dumps(lottie)}
        }});
    </script>
</body>
</html>"""
    
    return json.dumps({
        "lottie_json": lottie,
        "preview_html": preview_html,
        "usage": {
            "description": f"形状变化动画：{start_shape} → {end_shape}",
            "duration": f"{duration}秒"
        }
    }, indent=2)


# 更新 ANIMATION_TOOLS 列表
ADVANCED_TOOLS = [
    {
        "name": "generate_lottie_path_animation",
        "description": "生成 SVG 路径绘制动画（Lottie 格式）。支持自定义 SVG 路径，自动生成描边动画效果。",
        "parameters": {
            "type": "object",
            "properties": {
                "path_data": {
                    "type": "string",
                    "description": "SVG 路径数据（d 属性），如：'M 100,100 L 200,100 L 150,50 Z'"
                },
                "duration": {
                    "type": "number",
                    "default": 2.0,
                    "description": "动画持续时间（秒）"
                },
                "stroke_width": {
                    "type": "number",
                    "default": 3.0,
                    "description": "描边宽度"
                },
                "stroke_color": {
                    "type": "string",
                    "default": "#4facfe",
                    "description": "描边颜色"
                },
                "fill_color": {
                    "type": "string",
                    "description": "填充颜色（可选）"
                },
                "width": {
                    "type": "integer",
                    "default": 400,
                    "description": "画布宽度"
                },
                "height": {
                    "type": "integer",
                    "default": 400,
                    "description": "画布高度"
                }
            },
            "required": ["path_data"]
        },
        "handler": generate_lottie_path_animation,
    },
    {
        "name": "generate_lottie_shape_morph",
        "description": "生成形状变化动画（Shape Morph）。支持圆形、方形、三角形、星形之间的平滑变换。",
        "parameters": {
            "type": "object",
            "properties": {
                "start_shape": {
                    "type": "string",
                    "enum": ["circle", "square", "triangle", "star"],
                    "description": "起始形状"
                },
                "end_shape": {
                    "type": "string",
                    "enum": ["circle", "square", "triangle", "star"],
                    "description": "结束形状"
                },
                "duration": {
                    "type": "number",
                    "default": 1.5,
                    "description": "动画持续时间（秒）"
                },
                "width": {
                    "type": "integer",
                    "default": 200,
                    "description": "画布宽度"
                },
                "height": {
                    "type": "integer",
                    "default": 200,
                    "description": "画布高度"
                },
                "color": {
                    "type": "string",
                    "default": "#4facfe",
                    "description": "填充颜色"
                }
            },
            "required": ["start_shape", "end_shape"]
        },
        "handler": generate_lottie_shape_morph,
    },
]
