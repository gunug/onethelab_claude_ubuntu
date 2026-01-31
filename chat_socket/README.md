# Chat Socket

Claude Code CLI를 웹 브라우저에서 사용할 수 있는 로컬 WebSocket 서버입니다.

## 사전 준비

다음 서비스에 가입이 필요합니다:

1. **Claude Code** (필수): https://claude.ai/download
2. **ngrok** (외부 접속 시): https://ngrok.com/

## 설치

```bash
install.bat
```
Python, Node.js, ngrok, aiohttp, Claude CLI를 자동 설치합니다.

## 설정 (외부 접속 시)

```bash
config.bat
```
ngrok authtoken, domain, OAuth를 설정합니다.

## 실행

**로컬 실행:**
```bash
run.bat
```
브라우저에서 http://localhost:8765 접속

**외부 접속:**
```bash
run_ngrok.bat
```
브라우저에서 ngrok URL 접속

## 문제 해결

### ngrok 접속 시 OAuth state error 발생

ngrok 터널을 재시작한 후 접속할 때 OAuth state error가 발생할 수 있습니다.

**원인**: 브라우저에 저장된 이전 세션의 OAuth 쿠키가 새 터널 세션과 충돌

**해결 방법**:
1. 브라우저 쿠키 삭제 후 재접속
   - Chrome: `F12` → Application → Cookies → ngrok 관련 쿠키 삭제
   - 또는 `Ctrl+Shift+Delete` → 쿠키 삭제
2. 시크릿/프라이빗 창에서 접속
