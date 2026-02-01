# Docker 설정 문제 해결 가이드

Docker 컨테이너로 Claude Chat Server를 설정하면서 발생한 문제들과 해결 방법을 정리한 문서입니다.

---

## 1. CPU 리소스 오류

### 증상
```
docker: Error response from daemon: range of CPUs is from 0.01 to 1.00, as there are only 1 CPUs available
```

### 원인
서버에 CPU가 1개뿐인데 `docker-compose.yml`과 `docker-run.sh`에서 CPU를 2개로 설정함.

### 해결
```yaml
# docker-compose.yml
deploy:
  resources:
    limits:
      cpus: '1'  # 2 -> 1로 변경
```

```bash
# docker-run.sh
--cpus 1  # 2 -> 1로 변경
```

---

## 2. 인증 파일 권한 오류

### 증상
```
cat: /home/appuser/.claude/.credentials.json: Permission denied
```
컨테이너 내부에서 Claude CLI 인증 실패.

### 원인
호스트의 `~/.claude/.credentials.json` 파일이 600 권한(소유자만 읽기)으로 설정되어 있어서, 컨테이너 내부의 `appuser`가 읽을 수 없음.

### 해결
인증 파일을 프로젝트 폴더에 복사하고 권한 변경:
```bash
cp ~/.claude/.credentials.json /home/onethelab_admin/onethelab_claude_ubuntu/.credentials.json
chmod 644 /home/onethelab_admin/onethelab_claude_ubuntu/.credentials.json
```

docker-run.sh에서 마운트 경로 변경:
```bash
-v ./.credentials.json:/home/appuser/.claude/.credentials.json:ro
```

**주의**: `.credentials.json`을 `.gitignore`에 추가하여 Git에 커밋되지 않도록 해야 함.

---

## 3. tmpfs 권한 오류

### 증상
```
ls: cannot open directory '/home/appuser/.claude/': Permission denied
```
컨테이너 내부에서 `.claude` 디렉토리 접근 불가.

### 원인
tmpfs 마운트 시 기본적으로 root 소유로 생성되어 `appuser`(uid=1000)가 접근할 수 없음.

### 해결
tmpfs 마운트 시 uid/gid 명시:
```bash
--tmpfs /tmp:size=100M,mode=1777,uid=1000,gid=1000
--tmpfs /home/appuser/.claude:size=10M,mode=0700,uid=1000,gid=1000
```

**참고**: `appuser`의 uid/gid 확인:
```bash
docker run --rm claude-chat-server id appuser
# uid=1000(appuser) gid=1000(appuser)
```

---

## 4. Claude CLI 테스트 실패

### 증상
```
[테스트] claude "test"
Claude CLI: 실패 - claude CLI를 확인하세요.
```

### 원인
`claude "test"` 명령은 대화형 모드로 실행되어 stdin 입력을 기다림. 타임아웃 발생.

### 해결
테스트 명령을 `claude --version`으로 변경:
```python
# server.py
def test_claude_cli():
    cmd = 'claude --version'  # "claude \"test\"" -> "claude --version"
    # ...
```

---

## 5. read-only 파일시스템으로 인한 Claude CLI 출력 없음 (핵심 문제)

### 증상
```
[DEBUG] stdout 읽기 시작, process.poll()=None
[DEBUG] stdout EOF, 총 0줄 읽음
```
Claude CLI가 실행은 되지만 출력이 전혀 없음. WebSocket으로 응답이 오지 않음.

### 원인
`--read-only` 옵션으로 컨테이너 파일시스템을 읽기 전용으로 설정했는데, Claude CLI (Node.js 기반)가 내부적으로 파일 쓰기를 시도함. 쓰기 실패 시 조용히 종료됨 (exit code 0).

### 진단 방법
```bash
# read-only 없이 테스트 - 정상 작동
docker run --rm ... claude-chat-server python3 test_claude.py
# 출력: [0] {"type":"system",...}

# read-only 추가 테스트 - 출력 없음
docker run --rm --read-only ... claude-chat-server python3 test_claude.py
# 출력: EOF at line 0
```

### 해결
`--read-only` 옵션 제거:
```bash
# docker-run.sh
docker run -d \
    --name claude-chat-server \
    --security-opt no-new-privileges:true \
    # --read-only  # 이 줄 제거
    ...
```

```yaml
# docker-compose.yml
security_opt:
  - no-new-privileges:true
# read_only: true  # 이 줄 주석처리 또는 제거
```

**보안 참고**: `--read-only`를 제거해도 Docker 컨테이너 격리는 유지됨. `no-new-privileges` 옵션으로 권한 상승은 여전히 차단됨.

---

## 6. 환경 변수 누락

### 증상
컨테이너 로그가 비어 있거나, Python 출력이 버퍼링됨.

### 해결
docker-run.sh에 환경 변수 추가:
```bash
-e HOME=/home/appuser \
-e PYTHONUNBUFFERED=1 \
```

---

## 7. ccusage 오류 (사용량 표시 기능)

### 증상
```
npm error enoent: mkdir '/home/appuser/.npm'
Error: No valid Claude data directories found
```

### 원인
1. ccusage가 `.claude/projects` 디렉토리에 접근해야 하는데 컨테이너에 마운트되지 않음
2. 호스트와 컨테이너의 uid 불일치로 권한 문제 발생

### 해결

**1단계: 호스트의 .claude 디렉토리 마운트**
```bash
# docker-run.sh
-v ~/.claude:/home/appuser/.claude \  # 전체 디렉토리 마운트 (쓰기 가능)
```

**2단계: projects 디렉토리 권한 변경**
```bash
chmod -R 755 ~/.claude/projects
```

**3단계: uid 일치시키기**

호스트 사용자 uid 확인:
```bash
id $(whoami)
# uid=1001(onethelab_admin)
```

Dockerfile에서 appuser uid를 호스트와 일치시킴:
```dockerfile
# non-root 사용자 생성 (호스트 사용자와 uid 일치시킴)
RUN useradd -m -s /bin/bash -u 1001 appuser
```

docker-run.sh tmpfs uid도 변경:
```bash
--tmpfs /tmp:size=100M,mode=1777,uid=1001,gid=1001 \
```

**4단계: 이미지 재빌드 (캐시 없이)**
```bash
docker build --no-cache -t claude-chat-server .
```

### 확인
로그에서 사용량이 정상 표시되면 성공:
```
[DEBUG] 사용량 전송: 오늘 $11.40 (₩16,302)
[DEBUG] 블록 전송: $11.40, 남은 시간: 156분
```

---

## 최종 docker-run.sh 설정

```bash
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
    --restart unless-stopped \
    claude-chat-server
```

**주의**: uid=1001은 호스트 사용자의 uid와 일치해야 함. `id $(whoami)`로 확인.

---

## 문제 해결 체크리스트

| 문제 | 확인 방법 | 해결 |
|------|----------|------|
| CPU 오류 | `nproc` 명령으로 CPU 개수 확인 | `--cpus` 값 조정 |
| 인증 오류 | 컨테이너 내부에서 `cat .credentials.json` | 파일 복사 및 권한 변경 |
| tmpfs 권한 | `docker exec ... ls -la /home/appuser/.claude/` | uid/gid 옵션 추가 |
| CLI 테스트 | 로그에서 "Claude CLI: 실패" 확인 | 테스트 명령 변경 |
| 출력 없음 | 로그에서 "stdout EOF, 총 0줄" 확인 | `--read-only` 제거 |
| 로그 없음 | `docker logs` 출력 확인 | `PYTHONUNBUFFERED=1` 추가 |
| ccusage 오류 | 로그에서 "No valid Claude data directories" | .claude 전체 마운트 + uid 일치 |
