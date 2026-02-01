# Claude Code Remote Access

Ubuntu 서버에서 Docker 컨테이너로 격리된 Claude Code CLI 환경을 웹 브라우저로 원격 접근하는 프로젝트입니다.

## 프로젝트 목적

- **서버 기반 원격 접근**: Ubuntu 서버에 Claude Code CLI 환경을 구축하고, HTTPS로 안전하게 접근
- **Docker 격리**: 보안을 위해 Docker 컨테이너 내에서 Claude CLI 실행
- **Google OAuth 인증**: 허용된 이메일만 접근 가능
- **실시간 통신**: WebSocket을 통해 브라우저와 Claude CLI 간 실시간 메시지 전송

## 시스템 구조

```
[브라우저] ←─ HTTPS ─→ [Nginx:443] ←─ HTTP ─→ [Docker:8765] ←─ CLI ─→ [Claude]
                        (SSL/TLS)              (Python 서버)
```

### 구성 요소

1. **Nginx**: HTTPS 처리 및 리버스 프록시 (443 → 8765)
2. **Docker 컨테이너**: Python 서버 + Claude CLI 격리 실행
3. **Google OAuth**: 사용자 인증 (허용 이메일 화이트리스트)
4. **Let's Encrypt**: 무료 SSL 인증서 (자동 갱신)

## 주요 기능

- **HTTPS 보안 통신**: Let's Encrypt SSL 인증서
- **Google OAuth 2.0**: 허용된 이메일만 로그인 가능
- **실시간 WebSocket**: 양방향 메시지 전송
- **Claude AI 통합**: Claude CLI 스트리밍 응답
- **진행 상황 표시**: 도구 호출, 비용, 토큰 실시간 확인
- **세션 관리**: 대화 컨텍스트 유지
- **요청 대기열**: 여러 요청 순차 처리
- **사용량 모니터링**: 5시간 블록 사용량, 남은 시간 표시
- **PWA 지원**: 모바일에서 앱처럼 설치 가능
- **Docker 격리**: 보안을 위한 컨테이너 기반 실행

## 프로젝트 구조

```
onethelab_claude_ubuntu/
├── Dockerfile              # Docker 이미지 정의
├── docker-compose.yml      # Docker Compose 설정
├── docker-run.sh           # Docker 빌드 및 실행
├── docker-stop.sh          # Docker 컨테이너 중지
├── docker-reset.sh         # Docker 초기화 (컨테이너/이미지 삭제)
├── .dockerignore           # Docker 빌드 제외 파일
├── .env.example            # 환경 변수 예시 (OAuth 설정)
├── nginx-site.conf         # Nginx 사이트 설정
├── workspace/              # Claude 작업 디렉토리 (컨테이너에 마운트)
├── chat_socket/            # WebSocket 채팅 서버
│   ├── server.py           # Python 통합 서버 (HTTP + WebSocket + OAuth)
│   ├── index.html          # 웹 채팅 인터페이스
│   ├── auth/               # Google OAuth 인증 모듈
│   │   ├── __init__.py
│   │   ├── oauth.py        # Google OAuth 로직
│   │   └── session.py      # 메모리 기반 세션 관리
│   ├── templates/          # HTML 템플릿
│   │   └── login.html      # 로그인 페이지
│   ├── manifest.json       # PWA 설정
│   ├── service-worker.js   # PWA 서비스 워커
│   ├── icons/              # PWA 앱 아이콘
│   └── docs/               # 문서 폴더
├── CLAUDE.md               # Claude Code 작업 지침
└── README.md               # 프로젝트 소개 문서
```

## 요구 사항

### 서버 요구 사항
- Ubuntu 20.04 이상
- Docker 20.10 이상
- Nginx
- Certbot (Let's Encrypt)
- 도메인 (SSL 인증서 발급용)

### 외부 서비스
- Google Cloud Console 계정 (OAuth 클라이언트 ID)
- Anthropic 계정 (Claude CLI 인증)

## 설치 및 실행

### 1. 프로젝트 다운로드

```bash
git clone https://github.com/gunug/onethelab_claude_ubuntu.git
cd onethelab_claude_ubuntu
```

### 2. Docker 설치

```bash
curl -fsSL https://get.docker.com | sudo sh
sudo usermod -aG docker $USER
newgrp docker  # 또는 재로그인
```

### 3. Claude CLI 인증 (호스트에서)

```bash
npx @anthropic-ai/claude-code  # 로그인하여 ~/.claude/.credentials.json 생성
```

### 4. Google OAuth 설정

1. [Google Cloud Console](https://console.cloud.google.com/apis/credentials)에서 OAuth 2.0 클라이언트 ID 생성
2. 승인된 리디렉션 URI 추가: `https://your-domain.com/auth/google/callback`
3. `.env` 파일 생성:

```bash
cp .env.example .env
# .env 파일 편집하여 실제 값 입력
```

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
ALLOWED_EMAILS=admin@gmail.com,user@gmail.com
SESSION_SECRET=your-random-secret-key
```

### 5. Nginx + SSL 설정

```bash
# Nginx, Certbot 설치
sudo apt install -y nginx certbot python3-certbot-nginx

# SSL 인증서 발급
sudo certbot certonly --standalone -d your-domain.com

# Nginx 설정 복사
sudo cp nginx-site.conf /etc/nginx/sites-available/your-domain.com
sudo ln -sf /etc/nginx/sites-available/your-domain.com /etc/nginx/sites-enabled/
sudo rm -f /etc/nginx/sites-enabled/default

# Nginx 시작
sudo nginx -t && sudo systemctl restart nginx
```

### 6. Docker 실행

```bash
./docker-run.sh     # 빌드 및 실행
./docker-stop.sh    # 중지
./docker-reset.sh   # 초기화 (문제 발생 시)
```

### 7. 접속

브라우저에서 `https://your-domain.com` 접속

## 사용 방법

### 기본 사용

1. 브라우저에서 도메인 접속
2. Google 계정으로 로그인 (허용된 이메일만)
3. 메시지 입력란에 질문/명령 입력
4. Claude Code가 실시간으로 응답

### 명령어

| 명령어 | 설명 |
|--------|------|
| `/clear` | 세션 초기화 (대화 기록 삭제) |

### 인터페이스 기능

- **진행 상황 표시**: Claude가 사용하는 도구(파일 읽기, 편집 등) 실시간 확인
- **요청 대기열**: 여러 요청을 큐에 추가하여 순차 처리
- **사용량 모니터링**: 헤더에서 API 사용량 및 남은 시간 확인
- **알림음**: 대기열 완료 시 알림 (토글 가능)
- **사용자 정보**: 헤더에 로그인한 사용자 정보 및 로그아웃 버튼

## 보안

### Docker 컨테이너 격리

- `--security-opt no-new-privileges`: 권한 상승 금지
- `--memory 1g --cpus 1`: 리소스 제한
- `workspace/`: 작업 폴더만 쓰기 가능 (호스트에 마운트)

### 보안 위협 및 대응

| 위협 | Docker 없이 | Docker 있을 때 |
|------|------------|---------------|
| `rm -rf /` | 호스트 전체 삭제 | 컨테이너 내부만 영향 |
| SSH 키 삽입 | 호스트 탈취 가능 | 호스트 접근 불가 |
| reverse shell | 호스트 쉘 획득 | 컨테이너 쉘만 획득 |

### 공격 시 복구

```bash
./docker-reset.sh   # 컨테이너/이미지 삭제
./docker-run.sh     # 깨끗한 이미지로 재시작
```

## 문제 해결

### Docker 컨테이너가 시작되지 않음

```bash
# 로그 확인
docker logs claude-chat-server

# 컨테이너 상태 확인
docker ps -a
```

### SSL 인증서 갱신

Let's Encrypt 인증서는 90일마다 갱신 필요:

```bash
sudo certbot renew
```

자동 갱신 확인:
```bash
sudo systemctl status certbot.timer
```

## 기술 스택

- **Server**: Ubuntu, Docker, Nginx
- **Backend**: Python, aiohttp (HTTP + WebSocket 통합 서버)
- **Auth**: Google OAuth 2.0, 메모리 기반 세션
- **Frontend**: HTML, CSS, JavaScript, marked.js
- **AI**: Claude Code CLI (Anthropic)
- **SSL**: Let's Encrypt (Certbot)

## 버전 히스토리

### v4.2 (2026-02-01) - HTTPS 지원
- Let's Encrypt SSL 인증서 (sub.onethelab.com)
- Nginx 리버스 프록시 (443 → 8765)
- WebSocket over HTTPS (wss://) 지원

### v4.1 (2026-02-01) - Google OAuth 인증
- Google OAuth 2.0 인증 추가
- 허용 이메일 화이트리스트
- 로그인 페이지 및 사용자 UI

### v4.0 (2026-02-01) - Ubuntu 서버 이전
- Ubuntu 서버 배포 (Windows에서 이전)
- Docker 컨테이너 격리 환경
- ngrok 제거, 직접 IP 접속 방식

### v3.x 이전 버전
- Windows 기반 로컬 실행
- ngrok 터널링 지원

## 라이선스

개인 학습 및 실험 목적으로 제작되었습니다.
