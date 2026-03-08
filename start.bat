@echo off
chcp 65001 >nul
title AITeam - 一键启动

echo.
echo ====================================================
echo            AITeam 一键启动脚本
echo ====================================================
echo.

:: 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Python，请先安装 Python 3.9+
    pause
    exit /b 1
)

:: 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未检测到 Node.js，请先安装 Node.js 18+
    pause
    exit /b 1
)

echo [1/2] 启动后端服务...
start "AITeam Backend" cmd /k "cd /d %~dp0backend && if not exist venv python -m venv venv && call venv\Scripts\activate.bat && pip install -r requirements.txt -q && uvicorn app.main:app --reload --port 8000"

echo [信息] 等待后端启动...
timeout /t 8 /nobreak >nul

echo [2/2] 启动前端服务...
start "AITeam Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

echo.
echo ====================================================
echo   服务启动完成
echo ----------------------------------------------------
echo   后端地址: http://localhost:8000
echo   前端地址: http://localhost:5173
echo   API文档:  http://localhost:8000/docs
echo ====================================================
echo.
echo [提示] 按任意键打开浏览器...
pause >nul

start http://localhost:5173

echo [完成] 可以关闭此窗口
