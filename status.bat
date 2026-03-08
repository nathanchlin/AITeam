@echo off
chcp 65001 >nul
title AITeam - 查看状态

echo.
echo ====================================================
echo            AITeam 服务状态检查
echo ====================================================
echo.

echo [检查] 后端服务 Python/Uvicorn...
tasklist 2>nul | findstr "python.exe" >nul
if %errorlevel% neq 0 (
    echo   状态: 运行中
    netstat -ano | findstr ":8000" | findstr "LISTENING" >nul
    if %errorlevel% neq 0 (
        echo   端口 8000: 已监听
    ) else (
        echo   端口 8000: 未监听
    )
) else (
    echo   状态: 未运行
)

echo.
echo [检查] 前端服务 Node/Vite...
tasklist 2>nul | findstr "node.exe" >nul
if %errorlevel% neq 0 (
    echo   状态: 运行中
    netstat -ano | findstr ":5173" | findstr "LISTENING" >nul
    if %errorlevel% neq 0 (
        echo   端口 5173: 已监听
    ) else (
        echo   端口 5173: 未监听
    )
) else (
    echo   状态: 未运行
)

echo.
echo ====================================================
echo.
pause
