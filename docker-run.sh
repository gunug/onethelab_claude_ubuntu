#!/bin/bash

# Claude Chat Server - Docker 실행 스크립트

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "========================================"
echo "Claude Chat Server - Docker"
echo "========================================"

# Claude 인증 확인
if [ ! -f ~/.claude/.credentials.json ]; then
    echo -e "${RED}[오류] Claude 인증 정보가 없습니다.${NC}"
    echo "먼저 'claude' 명령으로 로그인하세요."
    exit 1
fi
echo -e "${GREEN}[OK] Claude 인증 확인${NC}"

# workspace 폴더 생성
mkdir -p ./workspace
echo -e "${GREEN}[OK] workspace 폴더 확인${NC}"

# 기존 컨테이너 정리
if docker ps -a --format '{{.Names}}' | grep -q '^claude-chat-server$'; then
    echo "[정리] 기존 컨테이너 중지/삭제..."
    docker stop claude-chat-server 2>/dev/null || true
    docker rm claude-chat-server 2>/dev/null || true
fi

# 이미지 빌드
echo "[빌드] Docker 이미지 빌드 중..."
docker build -t claude-chat-server .

# .env 파일에서 환경 변수 로드 (있는 경우)
ENV_ARGS=""
if [ -f .env ]; then
    echo -e "${GREEN}[OK] .env 파일 발견${NC}"
    # .env 파일의 각 줄을 -e 옵션으로 변환
    while IFS= read -r line || [ -n "$line" ]; do
        # 주석과 빈 줄 제외
        if [[ ! "$line" =~ ^# ]] && [[ -n "$line" ]]; then
            ENV_ARGS="$ENV_ARGS -e $line"
        fi
    done < .env
fi

# 컨테이너 실행
echo "[실행] 컨테이너 시작..."
docker run -d \
    --name claude-chat-server \
    --security-opt no-new-privileges:true \
    --tmpfs /tmp:size=100M,mode=1777,uid=1001,gid=1001 \
    -v ~/.claude:/home/appuser/.claude \
    -v ./workspace:/app/workspace \
    -p 8765:8765 \
    --memory 1g \
    --cpus 1 \
    -e HOME=/home/appuser \
    -e PYTHONUNBUFFERED=1 \
    $ENV_ARGS \
    --restart unless-stopped \
    claude-chat-server

echo ""
echo "========================================"
echo -e "${GREEN}서버 시작 완료!${NC}"
echo "========================================"
echo "접속: http://localhost:8765"
echo "외부: http://$(curl -s ifconfig.me 2>/dev/null || echo 'IP확인필요'):8765"
echo ""
echo "로그 확인: docker logs -f claude-chat-server"
echo "중지: docker stop claude-chat-server"
echo "삭제 후 재시작: ./docker-run.sh"
echo "========================================"
