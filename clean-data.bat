@echo off
chcp 65001 >nul
title AITeam - 清理数据

echo.
echo ====================================================
echo            AITeam 数据清理脚本
echo ====================================================
echo.
echo [警告] 此操作将清除以下数据:
echo   - Pipeline 计划数据 plans.json
echo   - 生成的代码输出 outputs/*
echo   - 前端构建缓存 dist/ 和 .vite/
echo.
echo [提示] Agent 数据 agents.json 将保留
echo.

set /p confirm="确认清理数据? 输入 y 继续: "
if /i not "%confirm%"=="y" (
    echo [取消] 操作已取消
    pause
    exit /b 0
)

echo.
echo [清理] Pipeline 计划数据...
if exist "%~dp0backend\app\data\plans.json" (
    del /f "%~dp0backend\app\data\plans.json"
    echo   已删除 plans.json
)

echo [清理] 输出目录...
if exist "%~dp0backend\app\data\outputs" (
    rd /s /q "%~dp0backend\app\data\outputs"
    echo   已清理 outputs 目录
)

echo [清理] 前端缓存...
if exist "%~dp0frontend\dist" (
    rd /s /q "%~dp0frontend\dist"
    echo   已清理 dist 目录
)
if exist "%~dp0frontend\node_modules\.vite" (
    rd /s /q "%~dp0frontend\node_modules\.vite"
    echo   已清理 .vite 缓存
)

echo.
echo ====================================================
echo   数据清理完成
echo ====================================================
echo.
pause
