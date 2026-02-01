#!/bin/bash

# Claude Chat Server - Docker 중지 스크립트

echo "========================================"
echo "Claude Chat Server - 중지"
echo "========================================"

if docker ps --format '{{.Names}}' | grep -q '^claude-chat-server$'; then
    echo "[중지] 컨테이너 중지 중..."
    docker stop claude-chat-server
    echo "[완료] 컨테이너 중지됨"
else
    echo "[정보] 실행 중인 컨테이너가 없습니다."
fi
