@echo off
chcp 65001 >nul
title AITeam - 重启服务

echo.
echo ====================================================
echo            AITeam 重启服务脚本
echo ====================================================
echo.

echo [信息] 停止所有服务...
taskkill /f /im python.exe >nul 2>&1
taskkill /f /im node.exe >nul 2>&1

echo [信息] 等待 2 秒...
timeout /t 2 /nobreak >nul

echo [信息] 重新启动服务...
call "%~dp0start.bat"
