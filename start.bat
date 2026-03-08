@echo off
chcp 65001 >nul
title AITeam - 一键启动

setlocal enabledelayedexpansion
set BACKEND_URL=http://localhost:8000
set MAX_WAIT=60
set CHECK_INTERVAL=2

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

:: 检查后端是否已运行
curl -s %BACKEND_URL%/docs >nul 2>&1
if not errorlevel 1 (
    echo [信息] 后端服务已在运行中
    goto :start_frontend
)

echo [1/2] 启动后端服务...

:: 创建 venv（如果不存在）
if not exist "%~dp0backend\venv" (
    echo [信息] 创建 Python 虚拟环境...
    cd /d "%~dp0backend"
    python -m venv venv
    if errorlevel 1 (
        echo [错误] 创建虚拟环境失败
        pause
        exit /b 1
    )
)

:: 安装依赖
echo [信息] 检查后端依赖...
cd /d "%~dp0backend"
call venv\Scripts\activate.bat
pip install -r requirements.txt -q 2>nul
if errorlevel 1 (
    echo [警告] 依赖安装可能有警告，继续启动...
)

:: 启动后端
start "AITeam Backend" cmd /k "cd /d %~dp0backend && call venv\Scripts\activate.bat && uvicorn app.main:app --reload --port 8000"

:: 等待后端就绪
echo [信息] 等待后端启动...
set /a waited=0
:wait_backend
curl -s %BACKEND_URL%/docs >nul 2>&1
if not errorlevel 1 (
    echo [成功] 后端服务已就绪
    goto :start_frontend
)
set /a waited+=CHECK_INTERVAL
if !waited! geq %MAX_WAIT% (
    echo [错误] 后端启动超时（等待了 %MAX_WAIT% 秒）
    echo [提示] 请检查 "AITeam Backend" 窗口中的错误信息
    pause
    exit /b 1
)
timeout /t %CHECK_INTERVAL% /nobreak >nul
goto :wait_backend

:start_frontend
echo [2/2] 启动前端服务...

:: 检查前端是否已运行
curl -s http://localhost:5173 >nul 2>&1
if not errorlevel 1 (
    echo [信息] 前端服务已在运行中
    goto :done
)

start "AITeam Frontend" cmd /k "cd /d %~dp0frontend && npm run dev"

:: 等待前端就绪
echo [信息] 等待前端启动...
set /a waited=0
:wait_frontend
curl -s http://localhost:5173 >nul 2>&1
if not errorlevel 1 (
    echo [成功] 前端服务已就绪
    goto :done
)
set /a waited+=CHECK_INTERVAL
if !waited! geq %MAX_WAIT% (
    echo [警告] 前端启动超时，但可能仍在启动中
    goto :done
)
timeout /t %CHECK_INTERVAL% /nobreak >nul
goto :wait_frontend

:done
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
