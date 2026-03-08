@echo off
chcp 65001 >nul
title AITeam - 停止服务

echo.
echo ====================================================
echo            AITeam 停止服务脚本
echo ====================================================
echo.

echo [信息] 停止后端服务 Python...
taskkill /f /im python.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [完成] 后端服务已停止
) else (
    echo [提示] 未找到运行中的 Python 进程
)

echo [信息] 停止前端服务 Node...
taskkill /f /im node.exe >nul 2>&1
if %errorlevel% equ 0 (
    echo [完成] 前端服务已停止
) else (
    echo [提示] 未找到运行中的 Node 进程
)

echo.
echo ====================================================
echo   所有服务已停止
echo ====================================================
echo.
pause
