#!/bin/bash

# 证券公司员工配偶信息报备系统启动脚本

echo "===================================="
echo "证券公司员工配偶信息报备系统"
echo "===================================="
echo
echo "正在启动前后端服务..."
echo

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "错误: 未检测到Node.js，请先安装Node.js"
    exit 1
fi

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "错误: 未检测到Python，请先安装Python 3.8+"
    exit 1
fi

# 检查前端依赖
if [ ! -d "node_modules" ]; then
    echo "正在安装前端依赖..."
    npm install
    if [ $? -ne 0 ]; then
        echo "前端依赖安装失败"
        exit 1
    fi
fi

# 检查后端依赖
if [ ! -d "backend/venv" ]; then
    echo "正在创建Python虚拟环境..."
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "后端依赖安装失败"
        exit 1
    fi
    cd ..
fi

echo
echo "依赖检查完成，正在启动服务..."
echo

# 启动后端服务
echo "启动后端服务 (端口: 8000)..."
cd backend
source venv/bin/activate
python start.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "等待后端服务启动..."
sleep 3

# 启动前端服务
echo "启动前端服务 (端口: 3000)..."
npm run dev &
FRONTEND_PID=$!

echo
echo "===================================="
echo "服务启动完成！"
echo "===================================="
echo "前端地址: http://localhost:3000"
echo "后端地址: http://localhost:8000"
echo "API文档: http://localhost:8000/docs"
echo "===================================="
echo
echo "按 Ctrl+C 停止所有服务"

# 等待用户中断
trap "echo '正在停止服务...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait