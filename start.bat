@echo off
chcp 65001 >nul
echo ====================================
echo 证券公司员工配偶信息报备系统
echo ====================================
echo.
echo 正在启动前后端服务...
echo.

REM 检查Node.js是否安装
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Node.js，请先安装Node.js
    pause
    exit /b 1
)

REM 检查Python是否安装
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo 错误: 未检测到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

REM 检查前端依赖
if not exist "node_modules" (
    echo 正在安装前端依赖...
    npm install
    if %errorlevel% neq 0 (
        echo 前端依赖安装失败
        pause
        exit /b 1
    )
)

REM 检查后端依赖
if not exist "backend\venv" (
    echo 正在创建Python虚拟环境...
    cd backend
    python -m venv venv
    call venv\Scripts\activate
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo 后端依赖安装失败
        pause
        exit /b 1
    )
    cd ..
)

echo.
echo 依赖检查完成，正在启动服务...
echo.

REM 启动后端服务
echo 启动后端服务 (端口: 8001)...
start "后端服务" cmd /k "cd backend && venv\Scripts\activate && python start.py"

REM 等待后端启动
echo 等待后端服务启动...
timeout /t 3 /nobreak >nul

REM 启动前端服务
echo 启动前端服务 (端口: 3000)...
start "前端服务" cmd /k "npm run dev"

echo.
echo ====================================
echo 服务启动完成！
echo ====================================
echo 前端地址: http://localhost:3000
echo 后端地址: http://localhost:8001
echo API文档: http://localhost:8001/docs
echo ====================================
echo.
echo 按任意键关闭此窗口...
pause >nul
