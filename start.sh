#!/bin/bash

# 证券公司员工配偶信息报备系统启动脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 端口配置
BACKEND_PORT=8001
FRONTEND_PORT=3000

echo "===================================="
echo "证券公司员工配偶信息报备系统"
echo "===================================="
echo
echo "正在启动前后端服务..."
echo

# 检查端口占用并清理的函数
check_and_kill_port() {
    local port=$1
    local service_name=$2
    
    local pid=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pid" ]; then
        echo -e "${YELLOW}警告: 端口 $port 被进程 $pid 占用，正在清理...${NC}"
        kill -9 $pid 2>/dev/null
        sleep 1
        
        # 再次检查
        local new_pid=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$new_pid" ]; then
            echo -e "${RED}错误: 无法清理端口 $port，请手动处理${NC}"
            exit 1
        else
            echo -e "${GREEN}端口 $port 清理成功${NC}"
        fi
    fi
}

# 清理端口
echo "检查并清理端口占用..."
check_and_kill_port $BACKEND_PORT "后端服务"
check_and_kill_port $FRONTEND_PORT "前端服务"

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
if [ ! -d "frontend-app/node_modules" ]; then
    echo "正在安装前端依赖..."
    cd frontend-app
    npm install
    if [ $? -ne 0 ]; then
        echo "前端依赖安装失败"
        exit 1
    fi
    cd ..
fi

# 检查后端依赖
if [ ! -d "backend-service/venv" ]; then
    echo "正在创建Python虚拟环境..."
    cd backend-service
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
echo "启动后端服务 (端口: $BACKEND_PORT)..."
cd backend-service
source venv/bin/activate
python start.py &
BACKEND_PID=$!
cd ..

# 等待后端启动
echo "等待后端服务启动..."
sleep 3

# 启动前端服务
echo "启动前端服务 (端口: $FRONTEND_PORT)..."
cd frontend-app
npm run dev &
FRONTEND_PID=$!
cd ..

echo
echo "===================================="
echo "服务启动完成！"
echo "===================================="
echo -e "前端地址: ${GREEN}http://localhost:$FRONTEND_PORT${NC}"
echo -e "后端地址: ${GREEN}http://localhost:$BACKEND_PORT${NC}"
echo -e "API文档: ${GREEN}http://localhost:$BACKEND_PORT/docs${NC}"
echo "===================================="
echo
echo "按 Ctrl+C 停止所有服务"

# 优雅停止函数
stop_services() {
    echo
    echo -e "${YELLOW}正在停止服务...${NC}"
    
    # 停止前端服务
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo -e "${GREEN}前端服务已停止${NC}"
    fi
    
    # 停止后端服务
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo -e "${GREEN}后端服务已停止${NC}"
    fi
    
    # 清理可能残留的进程
    sleep 1
    check_and_kill_port $BACKEND_PORT "后端服务" 2>/dev/null || true
    check_and_kill_port $FRONTEND_PORT "前端服务" 2>/dev/null || true
    
    echo -e "${GREEN}所有服务已停止${NC}"
    exit 0
}

# 等待用户中断
trap stop_services INT
wait