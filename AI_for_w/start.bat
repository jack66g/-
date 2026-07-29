@echo off
chcp 65001 >nul
title SmartWriter 一键启动

echo ============================================
echo   SmartWriter 智能写作平台 - 一键启动
echo ============================================
echo.

echo [1/3] 检查 MySQL 服务...
sc query MySQL80 | find "RUNNING" >nul
if errorlevel 1 (
    echo   - MySQL 未运行，正在尝试启动...
    net start MySQL80 2>nul
    if errorlevel 1 (
        echo   [警告] MySQL 启动失败！请手动启动 MySQL 服务后重试。
        echo   提示: Win+R 输入 services.msc，找到 MySQL80 并启动。
        pause
        exit /b 1
    )
)
echo   - MySQL 运行正常 √
echo.

echo [2/3] 启动后端 Django...
start "SmartWriter-Backend" cmd /k "cd /d E:\program\AI_for_w\SmartWriter_Backend && call venv\Scripts\activate && python manage.py runserver 8000"
echo   - 后端已在独立窗口启动 (http://localhost:8000)
echo.

echo [3/3] 启动前端 Vue...
start "SmartWriter-Frontend" cmd /k "cd /d E:\program\AI_for_w\smart-writer-web && npm run dev"
echo   - 前端已在独立窗口启动 (http://localhost:5173)
echo.

echo 等待服务启动中...
timeout /t 10 /nobreak >nul
echo.
echo 正在打开浏览器...
start http://localhost:5173
echo.
echo ============================================
echo   启动完成！
echo   前端页面: http://localhost:5173
echo   后端 API:  http://localhost:8000/api/
echo   后台管理: http://localhost:8000/admin/
echo ============================================
echo.
echo 关闭本窗口不影响服务运行。直接关闭后端/前端窗口即可停止对应服务。
echo.
pause
