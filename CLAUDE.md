# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## IMPORTANT

**각각의 수정사항의 마지막에 반드시 CLAUDE.md 파일을 업데이트할 것.**

**기능이 완성되면 git에 커밋할 것. 오류가 있거나 디버깅 중일 때는 커밋하지 말 것. 자동으로 GitHub에 push 하지 말것.**

**할 일을 물어보면 `chat_socket/docs/todo.md` 파일을 읽고 답할 것. 할 일 추가 요청 시 해당 파일에 추가할 것.**

**매 컨테이너 추가/삭제 시 반드시 CLAUDE.md의 "실행 중인 컨테이너 목록" 섹션을 업데이트할 것.**

---

## 현재 진행 상황 (Ubuntu 서버 이전 작업)

### 완료된 작업
1. ✅ Ubuntu 서버에 레포지토리 클론 및 새 레포 생성 (`onethelab_claude_ubuntu`)
2. ✅ ngrok 관련 파일 삭제 (`config.bat` 삭제, `install.bat`에서 ngrok 섹션 제거)
3. ✅ 보안 검토 완료
   - `--dangerously-skip-permissions` 사용 시 보안 위험 분석
   - Docker 컨테이너 격리 방식 채택
4. ✅ Docker 설치 완료 (Docker 29.2.0)
5. ✅ Docker 관련 파일 생성
   - `Dockerfile` - 컨테이너 이미지 정의
   - `docker-compose.yml` - 컨테이너 설정
   - `docker-run.sh` - 빌드 및 실행 스크립트
   - `docker-stop.sh` - 중지 스크립트
   - `docker-reset.sh` - 초기화 스크립트
   - `.dockerignore` - 빌드 제외 파일
6. ✅ Docker 그룹 권한 적용 완료
7. ✅ Docker 이미지 빌드 및 컨테이너 실행 테스트 완료
   - CPU 리소스 1개로 수정 (서버 사양 맞춤)
   - tmpfs uid/gid=1001 설정 (호스트 사용자와 일치)
   - `--read-only` 옵션 제거 (Claude CLI 파일 쓰기 필요)
   - CLI 테스트 `claude --version`으로 변경
8. ✅ ccusage 오류 해결
   - 호스트 ~/.claude 전체 마운트
   - Dockerfile에서 appuser uid=1001로 설정 (호스트와 일치)
   - projects 디렉토리 권한 755로 변경
9. ✅ Google OAuth 인증 구현
   - `chat_socket/auth/` 모듈 생성 (oauth.py, session.py)
   - `chat_socket/templates/login.html` 로그인 페이지
   - server.py에 OAuth 라우트 추가 (/login, /auth/google/*, /auth/logout, /auth/status)
   - index.html에 사용자 정보/로그아웃 UI 추가
   - docker-run.sh에 .env 파일 환경 변수 전달 추가
   - `.env.example` 파일 생성

### 다음 세션에서 할 일
- (현재 없음)

### 완료된 추가 작업
10. ✅ HTTPS 설정 완료
    - Let's Encrypt 인증서 발급 (sub.onethelab.com)
    - Nginx 리버스 프록시 설정 (443 → 8765)
11. ✅ Google OAuth 테스트 완료
    - https://sub.onethelab.com 접속 확인
    - Google 로그인 및 허용 이메일 인증 확인

### 서버 정보
- IP: 158.247.252.160
- 사용자: onethelab_admin
- 프로젝트 경로: `/home/onethelab_admin/onethelab_claude_ubuntu`
- SSH 포트: 2202

---

## 실행 중인 컨테이너 목록

| 컨테이너명 | 도메인 | 포트 (Nginx → Docker) | 환경 변수 파일 | workspace | 상태 |
|-----------|--------|----------------------|---------------|-----------|------|
| claude-chat-server | sub.onethelab.com | 443 → 8765 | .env | workspace/ | ✅ 실행 중 |

### 컨테이너 관리 명령어
```bash
# 컨테이너 상태 확인
docker ps -a

# 특정 컨테이너 로그 확인
docker logs <컨테이너명>

# 컨테이너 중지/시작
docker stop <컨테이너명>
docker start <컨테이너명>
```

---

## 다중 컨테이너 확장 시나리오

### 구조
```
                          ┌─ sub.onethelab.com ─→ [Container A:8765]
[브라우저] → [Nginx:443] ─┤
                          └─ sub2.onethelab.com ─→ [Container B:8766]
```

### 새 컨테이너 추가 시 필요 작업

1. **환경 변수 파일 생성**
   ```bash
   cp .env .env.site2
   # ALLOWED_EMAILS 등 수정
   ```

2. **Docker 실행 스크립트 생성** (또는 docker-compose.yml 확장)
   ```bash
   # docker-run-site2.sh 생성
   # 포트: 8766, 컨테이너명: claude-chat-server-2
   ```

3. **DNS 설정**
   - 새 도메인 A 레코드 → 서버 IP

4. **SSL 인증서 발급**
   ```bash
   sudo certbot certonly --standalone -d sub2.onethelab.com
   ```

5. **Nginx 설정 추가**
   - 새 도메인용 server 블록 생성
   - 프록시 대상 포트 변경 (8766)

6. **Google OAuth 콜백 URI 추가**
   - Google Cloud Console에서 새 도메인 콜백 URI 등록

7. **CLAUDE.md 업데이트**
   - 위 "실행 중인 컨테이너 목록" 테이블에 새 컨테이너 추가

### 고려사항
- Claude CLI 인증 (`~/.claude`)은 모든 컨테이너가 공유
- 동시 사용 시 세션 충돌 가능성 있음
- workspace는 컨테이너별로 분리 권장 (`workspace/`, `workspace2/`)

---

## Project Overview

Ubuntu 서버에서 Docker 컨테이너로 격리된 Claude Code 원격 접근 프로젝트.
Python 통합 서버(HTTP + WebSocket)로 브라우저에서 Claude CLI와 실시간 통신.

## Project Structure

```
onethelab_claude_ubuntu/
├── Dockerfile            # Docker 이미지 정의
├── docker-compose.yml    # Docker Compose 설정
├── docker-run.sh         # Docker 빌드 및 실행
├── docker-stop.sh        # Docker 컨테이너 중지
├── docker-reset.sh       # Docker 초기화 (컨테이너/이미지 삭제)
├── .dockerignore         # Docker 빌드 제외 파일
├── .env.example          # 환경 변수 예시 (OAuth 설정)
├── workspace/            # Claude 작업 디렉토리 (컨테이너에 마운트)
├── chat_socket/          # WebSocket 채팅 서버
│   ├── server.py         # Python 통합 서버 (HTTP + WebSocket + OAuth)
│   ├── index.html        # 웹 채팅 인터페이스
│   ├── auth/             # Google OAuth 인증 모듈
│   │   ├── __init__.py
│   │   ├── oauth.py      # Google OAuth 로직
│   │   └── session.py    # 메모리 기반 세션 관리
│   ├── templates/        # HTML 템플릿
│   │   └── login.html    # 로그인 페이지
│   ├── manifest.json     # PWA 설정
│   ├── service-worker.js # PWA 서비스 워커
│   ├── icons/            # PWA 앱 아이콘
│   ├── install.bat       # Windows 의존성 설치 (Python, Node.js, aiohttp, Claude CLI)
│   ├── run.bat           # Windows 로컬 실행
│   ├── run_server_loop.bat # Windows 서버 재시작 루프
│   └── docs/             # 문서 폴더
├── CLAUDE.md             # Claude Code 지침
└── README.md             # 프로젝트 소개
```

## 시스템 구조

```
[브라우저] ←── HTTP + WebSocket ──→ [Docker 컨테이너] ←──CLI──→ [Claude]
                                    ├── Python 서버
                                    └── Claude CLI
                                    (포트 8765)
```

## 설치 방법 (Ubuntu)

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
claude  # 로그인하여 ~/.claude/.credentials.json 생성
```

## 실행 방법 (Ubuntu/Docker)

### Docker로 실행 (권장)
```bash
./docker-run.sh     # 빌드 및 실행
./docker-stop.sh    # 중지
./docker-reset.sh   # 초기화 (문제 발생 시)
```

### 직접 실행 (개발용, 보안 위험)
```bash
cd chat_socket
python3 server.py
```

### 접속
- 로컬: http://localhost:8765
- 외부: http://서버IP:8765 (방화벽 설정 필요)

## 설치 방법 (Windows)

### 1. 의존성 설치
```bash
cd chat_socket
install.bat  # Python, Node.js, aiohttp, Claude CLI 자동 설치
```

### 2. 실행
```bash
run.bat
```

## 보안 (Docker 격리)

### Docker 컨테이너 보안 설정
- `--read-only`: 파일시스템 읽기 전용
- `--security-opt no-new-privileges`: 권한 상승 금지
- `--memory 1g --cpus 2`: 리소스 제한
- `/tmp`, `/home/appuser/.claude`: tmpfs로 임시 쓰기만 허용
- `workspace/`: 작업 폴더만 쓰기 가능 (호스트에 마운트)

### 보안 위협 및 대응
| 위협 | Docker 없이 | Docker 있을 때 |
|------|------------|---------------|
| `rm -rf /` | 호스트 전체 삭제 | 컨테이너 내부만 영향 |
| SSH 키 삽입 | 호스트 탈취 가능 | ❌ 호스트 접근 불가 |
| reverse shell | 호스트 쉘 획득 | 컨테이너 쉘만 획득 |

### 공격 시 복구
```bash
./docker-reset.sh   # 컨테이너/이미지 삭제
./docker-run.sh     # 깨끗한 이미지로 재시작 (약 10초)
```

### Google OAuth 인증
- Google OAuth 2.0으로 사용자 인증
- 허용된 이메일만 접근 가능 (ALLOWED_EMAILS 환경 변수)
- 메모리 기반 세션 관리 (24시간 만료)

### 추가 보안 (TODO)
- [ ] Origin 검증 (CSWSH 방어)
- [ ] 명령어 블랙리스트 (위험 명령 차단)

## 주요 기능

- HTTP + WebSocket 통합 서버 (aiohttp, 포트 8765)
- Google OAuth 2.0 인증
  - `/login` : 로그인 페이지
  - `/auth/google/login` : OAuth 시작
  - `/auth/google/callback` : OAuth 콜백
  - `/auth/logout` : 로그아웃
  - `/auth/status` : 인증 상태 API
- `/` : index.html 자동 제공 (인증 필요)
- `/ws` : WebSocket 채팅 연결 (인증 필요)
- Claude CLI 스트리밍 연동
- 진행 상황 UI
  - 도구별 step 표시 (턴 번호, 아이콘, 완료 체크 ✓)
  - 스피닝 아이콘 + 프로그레스 바 애니메이션
  - 모델명 표시 (Opus/Sonnet/Haiku)
- Edit/Write/TodoWrite 도구 UI
  - Edit: 변경 전/후 diff 비교 (접기/펼치기)
  - Write: 파일 내용 표시 (접기/펼치기)
  - TodoWrite: 할 일 목록 (○ 대기/◐ 진행중/✓ 완료)
  - Bash: 명령어 별도 스타일 블록
- 완료 통계 (시간, 비용 USD/KRW, 토큰, 턴)
- /clear 명령어 (세션 리셋)
- 마크다운 렌더링, 자동 스크롤
- 모바일 반응형 UI (미디어 쿼리: 768px, 480px 브레이크포인트)
- 요청 대기열 기능
  - 여러 요청을 큐에 추가하여 순차 처리
  - 헤더 아래 대기열 UI (요청 수, 목록, 접기/펼치기)
  - 대기열 완료 시 알림음 (Web Audio API, 토글 지원)
- 사용량 표시 (ccusage 연동)
  - 접속 시 자동 사용량 조회
  - 요청 완료 시 사용량 갱신
  - 헤더에 블록 사용량, 리셋까지 남은 시간, 오늘 총 사용량 표시
- PWA (Progressive Web App) 지원
  - 안드로이드/iOS 홈 화면에 앱으로 설치 가능
  - manifest.json, service-worker.js
- 세션 자동 복구 기능
  - 타임아웃 발생 시 자동 세션 리셋
  - Claude CLI state/session error 감지 시 새 세션으로 자동 재시도

## Claude CLI 연동

- Claude CLI 세션 유지: 첫 요청은 `--session-id`로 새 세션 생성, 이후 요청은 `-r`로 세션 재개
- Claude CLI 권한: `--dangerously-skip-permissions` 옵션으로 모든 권한 자동 허용
- Claude CLI 프린트 모드: `-p -` 옵션으로 stdin에서 프롬프트 전달
- Claude CLI 진행 상황 실시간 표시 (stream-json 파싱)
  - 모델 정보, 도구 호출 상태, 완료 통계 (시간, 비용, 토큰)
  - 다양한 JSON 형식에 대한 방어적 타입 체크
  - Edit 도구 사용 시 변경 내용 (old_string, new_string) 출력
  - Write 도구 사용 시 파일 내용 표시 (최대 500자, 접기/펼치기 지원)
  - Bash 도구 사용 시 실행 명령어 표시 (최대 100자, 별도 스타일 블록)
  - TodoWrite 도구 사용 시 할 일 목록 표시 (상태별 아이콘, 접기/펼치기 지원)
- 비용 표시: USD와 원화(KRW) 동시 표시 (환율 상수: 1430원/USD, 2026년 1월 기준)
- 디버깅 로그: [DEBUG] 태그로 Python 콘솔에만 출력 (클라이언트 미전송)

## Claude Code 도구

상세 내용: [chat_socket/docs/claude_code_tools.md](chat_socket/docs/claude_code_tools.md)

## 알려진 문제

### 노트북 배터리 모드에서 WebSocket 연결 끊김
- **원인**: Windows 전원 관리가 Wi-Fi 어댑터를 절전 모드로 전환
- **증상**: 여러 WebSocket 연결이 동시에 끊김 (서버 문제 아님)
- **해결**: `Win + X` → 장치 관리자 (또는 `장치 관리자` → `네트워크 어댑터` → Wi-Fi → `속성` → `전원 관리`) → "전원을 절약하기 위해 컴퓨터가 이 장치를 끌 수 있음" 체크 해제
- 자세한 내용: [README.md 문제 해결](README.md#문제-해결)

## 버전 정보

### v4.2 (2026-02-01) - HTTPS 지원 추가
- **Let's Encrypt SSL 인증서**: sub.onethelab.com 도메인
- **Nginx 리버스 프록시**: 443 → 8765 포트 프록시
- **WebSocket over HTTPS**: wss:// 지원

### v4.1 (2026-02-01) - Google OAuth 인증 추가
- **Google OAuth 2.0 인증**: 허용된 이메일만 접근 가능
  - `chat_socket/auth/` 모듈 (oauth.py, session.py)
  - 로그인 페이지 (`templates/login.html`)
  - 메모리 기반 세션 관리 (24시간 만료)
- **환경 변수 지원**: `.env` 파일에서 OAuth 설정 로드
- **UI 업데이트**: 헤더에 사용자 정보 및 로그아웃 버튼 추가

### v4.0 (2026-02-01) - Ubuntu 서버 이전
- **Ubuntu 서버 배포**: Windows에서 Ubuntu 서버로 이전
- **Docker 컨테이너 격리**: 보안 강화를 위한 Docker 기반 실행 환경
  - read-only 파일시스템, 리소스 제한, 권한 상승 금지
  - workspace 폴더만 쓰기 가능
- **ngrok 제거**: 직접 IP 접속 방식으로 변경
- **보안 검토**: `--dangerously-skip-permissions` 위험성 분석 및 Docker로 완화

### v3.5 이전 버전
- Windows 기반 로컬 실행
- ngrok 터널링 지원
- Supabase Realtime (v2.5 이전, deprecated)
