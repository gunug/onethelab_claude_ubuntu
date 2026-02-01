#!/bin/bash

# Claude Chat Server - Docker 초기화 스크립트
# 컨테이너와 이미지를 삭제하고 새로 빌드

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Claude Chat Server - 초기화"
echo "========================================"
echo -e "${YELLOW}[경고] 컨테이너와 이미지를 삭제하고 새로 빌드합니다.${NC}"
echo ""

# 컨테이너 중지 및 삭제
if docker ps -a --format '{{.Names}}' | grep -q '^claude-chat-server$'; then
    echo "[삭제] 컨테이너 삭제..."
    docker stop claude-chat-server 2>/dev/null || true
    docker rm claude-chat-server 2>/dev/null || true
fi

# 이미지 삭제
if docker images --format '{{.Repository}}' | grep -q '^claude-chat-server$'; then
    echo "[삭제] 이미지 삭제..."
    docker rmi claude-chat-server 2>/dev/null || true
fi

# workspace 정리 (선택)
read -p "workspace 폴더도 초기화할까요? (y/N): " reset_workspace
if [ "$reset_workspace" = "y" ] || [ "$reset_workspace" = "Y" ]; then
    echo "[삭제] workspace 폴더 초기화..."
    rm -rf ./workspace
    mkdir -p ./workspace
fi

echo ""
echo -e "${GREEN}[완료] 초기화 완료${NC}"
echo ""
echo "다시 시작하려면: ./docker-run.sh"
echo "========================================"
