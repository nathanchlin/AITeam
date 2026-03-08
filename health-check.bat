@echo off
chcp 65001 >nul

echo [健康检查] 检查后端 API...
curl -s -o nul http://localhost:8000/ 2>nul
if %errorlevel% equ 0 (
    echo [成功] 后端 API 可访问
    goto :check_ws
) else (
    echo [失败] 后端 API 不可访问，    goto :health_check
)

:check_ws
echo [健康检查] 检查 WebSocket 端点...
curl -s -o nul -I "Upgrade: websocket" -H "Connection: Upgrade" http://localhost:8000/ws 2>nul
if %errorlevel% equ 0 (
    echo [成功] WebSocket 端点可用
    exit /b 0
) else (
    echo [等待] WebSocket 端点...
    timeout /t 2 /nobreak >nul
    goto :health_check
)

exit /b 1
