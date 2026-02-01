# Claude Code Chat Socket Server - Docker Image
FROM python:3.12-slim

# 환경 변수
ENV DEBIAN_FRONTEND=noninteractive
ENV NODE_VERSION=20

# 필수 패키지 설치
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Node.js 설치 (Claude CLI 필요)
RUN curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

# Python 패키지 설치
RUN pip install --no-cache-dir aiohttp

# Claude CLI 설치
RUN npm install -g @anthropic-ai/claude-code

# non-root 사용자 생성 (호스트 사용자와 uid 일치시킴)
RUN useradd -m -s /bin/bash -u 1001 appuser

# 작업 디렉토리 설정
WORKDIR /app

# 애플리케이션 파일 복사
COPY --chown=appuser:appuser chat_socket/ /app/chat_socket/
COPY --chown=appuser:appuser CLAUDE.md /app/

# Claude 설정 디렉토리 생성
RUN mkdir -p /home/appuser/.claude && chown -R appuser:appuser /home/appuser

# 사용자 전환
USER appuser

# 포트 노출
EXPOSE 8765

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8765/ || exit 1

# 실행
CMD ["python3", "chat_socket/server.py"]
