# Claude Code Remote Access

로컬 PC의 Claude Code CLI 환경을 외부에서 원격으로 접근하여 사용하기 위한 프로젝트입니다.

## 프로젝트 목적

- **로컬 개발환경 원격 접근**: 로컬 PC에 Claude Code CLI 환경을 구축하고, 외부에서 소켓 통신으로 로컬의 개발환경을 활용
- **실시간 통신**: Supabase Realtime Broadcast를 통해 외부 클라이언트와 로컬 Claude Code 간 실시간 메시지 전송
- **웹 기반 인터페이스**: 어디서든 브라우저로 접속하여 Claude Code와 상호작용

## 시스템 구조

```
┌─────────────────┐     Supabase Realtime     ┌─────────────────┐
│  HTML 클라이언트  │ ◄──── (WebSocket) ────► │   Python 봇     │
│  (외부 브라우저)  │       Broadcast          │   (로컬 PC)     │
└─────────────────┘                           └────────┬────────┘
                                                       │
                                                       ▼
                                              ┌─────────────────┐
                                              │  Claude Code    │
                                              │     CLI         │
                                              └─────────────────┘
```

### 연동 방식

1. **HTML 웹 클라이언트**: 외부에서 브라우저로 접속, Supabase Realtime에 연결
2. **Python 채팅봇**: 로컬 PC에서 실행, Supabase Realtime과 Claude Code CLI를 연결
3. **Supabase Realtime**: DB 없이 Broadcast 기능만 사용하여 WebSocket 통신 중계
4. **Claude Code CLI**: 로컬에서 실행되며 프린트 모드(`-p -`)로 프롬프트 수신 및 응답

## 주요 기능

- **실시간 통신**: Supabase Realtime Broadcast를 통한 WebSocket 기반 메시지 전송
- **Claude AI 통합**: Claude CLI를 활용한 AI 채팅봇 응답
- **세션 관리**: 대화 컨텍스트를 유지하는 세션 기능 (`--session-id`, `-r` 옵션)
- **진행 상황 표시**: Claude 응답 생성 과정을 실시간으로 확인 (도구 호출, 비용, 토큰)
- **마크다운 렌더링**: 채팅 메시지에 마크다운 문법 지원
- **요청 대기열**: 여러 요청을 순차 처리, 대기열 UI 표시
- **사용량 모니터링**: 5시간 블록 사용량, 오늘 총 사용량, 남은 시간 표시

## 프로젝트 구조

```
├── chat_bot/           # Python 채팅봇 클라이언트
│   ├── chat_bot.py     # Claude AI 연동 채팅봇
│   └── .env            # Supabase 연결 정보 (git 추적 제외)
├── chat_client/        # HTML/JS 웹 채팅 클라이언트
│   ├── index.html      # 웹 채팅 인터페이스
│   ├── chat.js         # 채팅 클라이언트 로직
│   └── config.js       # Supabase 연결 정보 (git 추적 제외)
├── supabase/           # Supabase 프로젝트 설정
├── project_docs/       # 프로젝트 문서
│   ├── install_list.md # 설치 절차 체크리스트
│   ├── python_chat_bot.md
│   ├── html_chat_client.md
│   └── claude_code_tools.md
├── run_chat_bot.bat    # Python 채팅봇 실행 스크립트
└── CLAUDE.md           # Claude Code 작업 지침
```

## 요구 사항

- Python 3.8 이상
- Node.js (Supabase CLI 설치용)
- Claude CLI (`npm install -g @anthropic-ai/claude-code`)
- Supabase 계정 및 프로젝트

## 설치 및 실행

### 1. 의존성 설치

```bash
# Python 패키지 설치
pip install realtime supabase python-dotenv

# Claude CLI 설치
npm install -g @anthropic-ai/claude-code
```

### 2. 환경 설정

**chat_bot/.env 파일 생성:**
```
SUPABASE_URL=your_supabase_url
SUPABASE_ANON_KEY=your_anon_key
CHANNEL_NAME=chat-room
```

**chat_client/config.js 파일 생성:**
```javascript
const SUPABASE_URL = 'your_supabase_url';
const SUPABASE_ANON_KEY = 'your_anon_key';
const CHANNEL_NAME = 'chat-room';
```

### 3. 실행

**Python 채팅봇 실행 (로컬 PC):**
```bash
run_chat_bot.bat
# 또는
python chat_bot/chat_bot.py
```

**웹 클라이언트 (외부):**
`chat_client/index.html` 파일을 웹 서버에 배포하거나 브라우저에서 열기

## 사용 방법

1. 로컬 PC에서 Python 채팅봇을 실행합니다.
2. 외부에서 웹 브라우저로 HTML 클라이언트에 접속합니다.
3. 이름을 입력하고 채팅을 시작합니다.
4. 메시지를 보내면 로컬의 Claude Code가 응답합니다.
5. `/clear` 명령어로 세션을 초기화할 수 있습니다.

## 기술 스택

- **Backend**: Python, Supabase Realtime
- **Frontend**: HTML, CSS, JavaScript, marked.js
- **AI**: Claude Code CLI (Anthropic)
- **통신**: WebSocket (Supabase Broadcast)

## 버전 히스토리

### v3.0 (2026-01-30) - 안정성 강화
- Python 봇: 토큰 자동 갱신 (45분마다), Heartbeat 모니터링 (30초마다)
- Python 봇: 절전 모드 복귀 시 자동 재연결
- HTML 클라이언트: 토큰 갱신 시 Realtime 자동 반영

### v2.2 (2026-01-30) - Railway 배포
- HTML 클라이언트 Railway 배포
- 배포 URL: https://onethelabsetting-production.up.railway.app
- Supabase Realtime Private Channel + RLS 적용

### v2.0 (2026-01-30) - Supabase Auth + MFA
- Supabase Auth 이메일/비밀번호 로그인
- MFA 지원 (TOTP 2단계 인증)
- 토큰 보안 강화 (Broadcast 노출 방지)

### v1.1 (2026-01-30) - 세션 클리어
- `/clear` 명령어로 Claude 세션 초기화
- 자동 스크롤 기능

### v1.0 (2026-01-29) - 초기 릴리즈
- Python 채팅봇 + HTML 클라이언트 실시간 통신
- Claude CLI 프린트 모드 (`-p -` stdin 방식)
- 진행 상황 UI, Edit diff 표시, 마크다운 렌더링

## 라이선스

개인 학습 및 실험 목적으로 제작되었습니다.
