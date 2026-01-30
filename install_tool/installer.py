"""
Claude Code Remote Access 설치 마법사
4단계: 설정 파일 생성
"""

import http.server
import socketserver
import webbrowser
import threading
import subprocess
import json
import urllib.parse
import os

PORT = 8888

HTML_CONTENT = """<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <title>Claude Code Remote Access Installer</title>
    <style>
        * {
            box-sizing: border-box;
        }
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 30px;
            background: #1a1a2e;
            color: #eee;
            line-height: 1.6;
        }
        h1 {
            color: #00d9ff;
            border-bottom: 2px solid #00d9ff;
            padding-bottom: 10px;
            margin-bottom: 30px;
        }
        h2 {
            color: #aaa;
            font-size: 14px;
            margin-bottom: 20px;
        }
        .step {
            background: #16213e;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            border-left: 4px solid #444;
        }
        .step.completed {
            border-left-color: #00ff88;
        }
        .step.current {
            border-left-color: #00d9ff;
            background: #1a2a4e;
        }
        .step.error {
            border-left-color: #ff4444;
        }
        .step-header {
            display: flex;
            align-items: center;
            gap: 15px;
        }
        .step-number {
            background: #444;
            color: #fff;
            width: 30px;
            height: 30px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 14px;
            flex-shrink: 0;
        }
        .step.completed .step-number {
            background: #00ff88;
            color: #000;
        }
        .step.current .step-number {
            background: #00d9ff;
            color: #000;
        }
        .step.error .step-number {
            background: #ff4444;
            color: #fff;
        }
        .step-title {
            font-size: 18px;
            font-weight: bold;
        }
        .step-desc {
            color: #aaa;
            margin-top: 10px;
            margin-left: 45px;
            font-size: 14px;
        }
        .step-actions {
            margin-top: 15px;
            margin-left: 45px;
        }
        button {
            background: #00d9ff;
            color: #000;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 14px;
            font-weight: bold;
            margin-right: 10px;
            margin-bottom: 5px;
        }
        button:hover {
            background: #00b8d9;
        }
        button:disabled {
            background: #444;
            color: #888;
            cursor: not-allowed;
        }
        button.running {
            background: #ffaa00;
            cursor: wait;
        }
        .status-bar {
            background: #0f0f1a;
            padding: 15px 20px;
            border-radius: 8px;
            margin-bottom: 30px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .status-text {
            color: #00ff88;
        }
        .status-text.error {
            color: #ff4444;
        }
        .status-text.running {
            color: #ffaa00;
        }
        .progress {
            color: #aaa;
        }
        .output-box {
            background: #0a0a15;
            border: 1px solid #333;
            border-radius: 5px;
            padding: 15px;
            margin-top: 15px;
            margin-left: 45px;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 12px;
            white-space: pre-wrap;
            word-break: break-all;
            max-height: 200px;
            overflow-y: auto;
            display: none;
        }
        .output-box.visible {
            display: block;
        }
        .output-box.success {
            border-color: #00ff88;
        }
        .output-box.error {
            border-color: #ff4444;
            color: #ff8888;
        }
        .spinner {
            display: inline-block;
            width: 14px;
            height: 14px;
            border: 2px solid #000;
            border-top-color: transparent;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-right: 8px;
            vertical-align: middle;
        }
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        .config-form {
            margin-top: 15px;
            margin-left: 45px;
            display: none;
        }
        .config-form.visible {
            display: block;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
            color: #aaa;
            font-size: 13px;
        }
        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #444;
            border-radius: 5px;
            background: #0a0a15;
            color: #eee;
            font-size: 14px;
            font-family: 'Consolas', 'Monaco', monospace;
        }
        .form-group input:focus {
            outline: none;
            border-color: #00d9ff;
        }
        .form-group input::placeholder {
            color: #666;
        }
        .form-row {
            display: flex;
            gap: 15px;
        }
        .form-row .form-group {
            flex: 1;
        }
        .form-hint {
            font-size: 11px;
            color: #666;
            margin-top: 3px;
        }
    </style>
</head>
<body>
    <h1>Claude Code Remote Access Installer</h1>
    <h2>user_install.md 기반 단계별 설치 가이드</h2>

    <div class="status-bar">
        <span class="status-text" id="statusText">준비됨</span>
        <span class="progress" id="progressText">0 / 5 단계 완료</span>
    </div>

    <div class="step completed" id="step1">
        <div class="step-header">
            <div class="step-number">✓</div>
            <div class="step-title">Python 설치</div>
        </div>
        <div class="step-desc">Python이 이미 설치되어 있습니다.</div>
    </div>

    <div class="step current" id="step2">
        <div class="step-header">
            <div class="step-number">2</div>
            <div class="step-title">Python 패키지 설치</div>
        </div>
        <div class="step-desc">realtime, supabase, python-dotenv 패키지를 설치합니다.</div>
        <div class="step-actions">
            <button onclick="runCommand('pip_install', this)">pip install 실행</button>
        </div>
        <div class="output-box" id="output2"></div>
    </div>

    <div class="step" id="step3">
        <div class="step-header">
            <div class="step-number">3</div>
            <div class="step-title">Node.js 및 CLI 도구 설치</div>
        </div>
        <div class="step-desc">Node.js 확인 후 없으면 자동 설치, 이후 Claude/Supabase/Railway CLI를 설치합니다.</div>
        <div class="step-actions">
            <button onclick="checkNode(this)" disabled id="btnCheckNode">Node.js 확인/설치</button>
            <button onclick="runCommand('install_claude', this)" disabled id="btnInstallClaude">Claude CLI 설치</button>
            <button onclick="checkWithFallback('check_supabase', this)" disabled id="btnSupabase">Supabase CLI</button>
            <button onclick="checkWithFallback('check_railway', this)" disabled id="btnRailway">Railway CLI</button>
        </div>
        <div class="output-box" id="output3"></div>
    </div>

    <div class="step" id="step4">
        <div class="step-header">
            <div class="step-number">4</div>
            <div class="step-title">Supabase 설정</div>
        </div>
        <div class="step-desc">Supabase 프로젝트 생성, 계정 설정, API 키 입력을 진행합니다.</div>
        <div class="step-actions">
            <button onclick="toggleConfigForm()" disabled id="btnConfigForm">설정 시작</button>
        </div>
        <div class="config-form" id="configForm">
            <!-- 가이드 섹션 -->
            <div style="background:#0a0a15; border:1px solid #333; border-radius:5px; padding:15px; margin-bottom:20px;">
                <h3 style="color:#00d9ff; margin:0 0 15px 0; font-size:14px;">📋 Supabase 설정 가이드</h3>

                <div style="margin-bottom:15px;">
                    <div style="color:#00ff88; font-weight:bold; margin-bottom:5px;">1단계: Supabase 프로젝트 생성</div>
                    <div style="color:#aaa; font-size:12px; margin-left:15px; margin-bottom:10px;">
                        • <a href="https://supabase.com" target="_blank" style="color:#00d9ff;">supabase.com</a> 접속 → 로그인 → New Project<br>
                        • 또는 아래에서 CLI로 프로젝트 생성 (supabase login 필요)
                    </div>
                    <div style="margin-left:15px; background:#16213e; padding:10px; border-radius:5px;" id="createProjectSection">
                        <div style="display:flex; gap:10px; margin-bottom:8px; flex-wrap:wrap;">
                            <select id="orgSelect" style="flex:1; min-width:150px; padding:8px; border:1px solid #444; border-radius:4px; background:#0a0a15; color:#eee; font-size:12px;">
                                <option value="">-- 조직 선택 --</option>
                            </select>
                            <button onclick="fetchOrgs()" style="padding:8px 12px; font-size:12px;">조직 목록</button>
                        </div>
                        <div style="display:flex; gap:10px; margin-bottom:8px; flex-wrap:wrap;">
                            <input type="text" id="newProjectName" placeholder="프로젝트 이름" style="flex:1; min-width:120px; padding:8px; border:1px solid #444; border-radius:4px; background:#0a0a15; color:#eee; font-size:12px;">
                            <input type="password" id="newProjectDbPassword" placeholder="DB 비밀번호" style="flex:1; min-width:120px; padding:8px; border:1px solid #444; border-radius:4px; background:#0a0a15; color:#eee; font-size:12px;">
                        </div>
                        <div style="display:flex; gap:10px; align-items:center;">
                            <select id="regionSelect" style="flex:1; padding:8px; border:1px solid #444; border-radius:4px; background:#0a0a15; color:#eee; font-size:12px;">
                                <option value="ap-northeast-1">도쿄 (ap-northeast-1)</option>
                                <option value="ap-northeast-2">서울 (ap-northeast-2)</option>
                                <option value="ap-southeast-1">싱가포르 (ap-southeast-1)</option>
                                <option value="us-east-1">미국 동부 (us-east-1)</option>
                                <option value="eu-west-1">유럽 (eu-west-1)</option>
                            </select>
                            <button onclick="createProject()" id="btnCreateProject" style="padding:8px 15px; font-size:12px; background:#00ff88; color:#000;">프로젝트 생성</button>
                        </div>
                    </div>
                </div>

                <div style="margin-bottom:15px;">
                    <div style="color:#00ff88; font-weight:bold; margin-bottom:5px;">2단계: 사용자 계정 생성 (웹 클라이언트용)</div>
                    <div style="color:#aaa; font-size:12px; margin-left:15px;">
                        • Supabase 대시보드 → Authentication → Users → Add user<br>
                        • 이메일/비밀번호 입력 → Auto Confirm User 체크 → Create user<br>
                        • 이 계정으로 웹 채팅 클라이언트에 로그인합니다
                    </div>
                </div>

                <div style="margin-bottom:15px;">
                    <div style="color:#00ff88; font-weight:bold; margin-bottom:5px;">3단계: 봇 계정 생성 (Python 봇용)</div>
                    <div style="color:#aaa; font-size:12px; margin-left:15px;">
                        • 위와 동일하게 Add user로 봇 전용 계정 생성<br>
                        • 예: bot@yourproject.com / 안전한 비밀번호<br>
                        • 이 계정 정보를 아래 폼에 입력합니다
                    </div>
                </div>

                <div>
                    <div style="color:#00ff88; font-weight:bold; margin-bottom:5px;">4단계: API 키 확인</div>
                    <div style="color:#aaa; font-size:12px; margin-left:15px;">
                        • Project Settings → API → Project URL, anon public 키 복사<br>
                        • 또는 아래 "CLI에서 가져오기" 버튼 사용 (supabase login 필요)
                    </div>
                </div>
            </div>

            <!-- 설정 입력 폼 -->
            <h3 style="color:#00d9ff; margin:0 0 15px 0; font-size:14px;">⚙️ 설정 입력</h3>

            <div class="form-group">
                <label>Supabase 프로젝트</label>
                <div style="display:flex; gap:10px;">
                    <select id="supabaseProject" style="flex:1; padding:10px; border:1px solid #444; border-radius:5px; background:#0a0a15; color:#eee; font-size:14px;">
                        <option value="">-- 프로젝트 선택 --</option>
                    </select>
                    <button onclick="fetchFromCLI()" id="btnFetchCLI" style="white-space:nowrap;">CLI에서 가져오기</button>
                </div>
                <div class="form-hint">Supabase CLI 로그인 필요: supabase login</div>
            </div>
            <div class="form-group">
                <label>Supabase URL</label>
                <input type="text" id="supabaseUrl" placeholder="https://xxxxx.supabase.co">
            </div>
            <div class="form-group">
                <label>Supabase Anon Key</label>
                <input type="text" id="supabaseAnonKey" placeholder="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...">
            </div>
            <div class="form-row">
                <div class="form-group">
                    <label>봇 이메일</label>
                    <input type="email" id="botEmail" placeholder="bot@example.com">
                </div>
                <div class="form-group">
                    <label>봇 비밀번호</label>
                    <input type="password" id="botPassword" placeholder="비밀번호">
                </div>
            </div>
            <div class="form-hint" style="margin-bottom:15px;">봇 계정은 위 가이드 3단계에서 생성한 계정 정보를 입력합니다.</div>

            <button onclick="saveConfig()" id="btnSaveConfig" style="width:100%; padding:12px; font-size:16px;">💾 설정 저장 및 다음 단계</button>
        </div>
        <div class="output-box" id="output4"></div>
    </div>

    <div class="step" id="step5">
        <div class="step-header">
            <div class="step-number">5</div>
            <div class="step-title">설치 완료</div>
        </div>
        <div class="step-desc">모든 설정이 완료되었습니다. 채팅봇을 실행할 수 있습니다.</div>
        <div class="step-actions">
            <button onclick="runCommand('run_bot', this)" disabled>채팅봇 실행</button>
        </div>
        <div class="output-box" id="output5"></div>
    </div>

    <script>
        let completedSteps = 1;  // Python 설치는 완료됨

        function updateProgress() {
            document.getElementById('progressText').textContent = `${completedSteps} / 5 단계 완료`;
        }

        function setStatus(text, type = 'normal') {
            const statusEl = document.getElementById('statusText');
            statusEl.textContent = text;
            statusEl.className = 'status-text';
            if (type === 'error') statusEl.classList.add('error');
            if (type === 'running') statusEl.classList.add('running');
        }

        async function runCommand(command, button) {
            const originalText = button.textContent;
            button.disabled = true;
            button.classList.add('running');
            button.innerHTML = '<span class="spinner"></span>실행 중...';
            setStatus('명령 실행 중...', 'running');

            try {
                const response = await fetch('/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                });
                const result = await response.json();

                // 출력 박스 찾기
                let outputBox = null;
                if (command === 'pip_install') outputBox = document.getElementById('output2');
                else if (command === 'check_node' || command === 'install_claude') outputBox = document.getElementById('output3');
                else if (command === 'run_bot') outputBox = document.getElementById('output5');

                if (outputBox) {
                    outputBox.textContent = result.output || result.error || '완료';
                    outputBox.classList.add('visible');
                    outputBox.classList.remove('success', 'error');
                    outputBox.classList.add(result.success ? 'success' : 'error');
                }

                if (result.success) {
                    setStatus('완료', 'normal');
                    button.textContent = '✓ 완료';
                    button.classList.remove('running');

                    // 단계 완료 처리
                    if (command === 'pip_install') {
                        completeStep(2);
                        enableStep(3);
                    } else if (command === 'install_claude') {
                        completeStep(3);
                        enableStep(4);
                    }
                } else {
                    setStatus('오류 발생', 'error');
                    button.textContent = originalText;
                    button.disabled = false;
                    button.classList.remove('running');
                }
            } catch (error) {
                setStatus('연결 오류', 'error');
                button.textContent = originalText;
                button.disabled = false;
                button.classList.remove('running');
                console.error(error);
            }
        }

        function completeStep(stepNum) {
            const step = document.getElementById('step' + stepNum);
            step.classList.remove('current');
            step.classList.add('completed');
            step.querySelector('.step-number').textContent = '✓';
            completedSteps = Math.max(completedSteps, stepNum);
            updateProgress();
        }

        function enableStep(stepNum) {
            const step = document.getElementById('step' + stepNum);
            step.classList.add('current');
            const buttons = step.querySelectorAll('button');
            buttons.forEach(btn => btn.disabled = false);
        }

        let supabaseProjects = [];  // 프로젝트 목록 저장

        function toggleConfigForm() {
            const form = document.getElementById('configForm');
            const btnForm = document.getElementById('btnConfigForm');

            if (form.classList.contains('visible')) {
                form.classList.remove('visible');
                btnForm.textContent = '설정 시작';
            } else {
                form.classList.add('visible');
                btnForm.textContent = '접기';
            }
        }

        async function fetchOrgs() {
            setStatus('조직 목록 가져오는 중...', 'running');
            const outputBox = document.getElementById('output4');

            try {
                const response = await fetch('/supabase_orgs', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                const result = await response.json();

                if (result.success && result.orgs) {
                    const select = document.getElementById('orgSelect');
                    select.innerHTML = '<option value="">-- 조직 선택 --</option>';
                    result.orgs.forEach(org => {
                        select.innerHTML += `<option value="${org.id}">${org.name}</option>`;
                    });
                    setStatus('조직 목록 로드 완료', 'normal');
                    outputBox.textContent = `${result.orgs.length}개 조직 로드됨`;
                    outputBox.classList.add('visible', 'success');
                    outputBox.classList.remove('error');
                } else {
                    setStatus('조직 목록 로드 실패', 'error');
                    outputBox.textContent = result.error || '조직 목록을 가져올 수 없습니다.';
                    outputBox.classList.add('visible', 'error');
                    outputBox.classList.remove('success');
                }
            } catch (error) {
                setStatus('연결 오류', 'error');
                console.error(error);
            }
        }

        async function createProject() {
            const orgId = document.getElementById('orgSelect').value;
            const projectName = document.getElementById('newProjectName').value.trim();
            const dbPassword = document.getElementById('newProjectDbPassword').value;
            const region = document.getElementById('regionSelect').value;

            if (!orgId) {
                alert('조직을 선택하세요. (조직 목록 버튼 클릭)');
                return;
            }
            if (!projectName) {
                alert('프로젝트 이름을 입력하세요.');
                return;
            }
            if (!dbPassword || dbPassword.length < 6) {
                alert('DB 비밀번호는 6자 이상 입력하세요.');
                return;
            }

            const btn = document.getElementById('btnCreateProject');
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span>생성 중...';
            setStatus('프로젝트 생성 중... (1-2분 소요)', 'running');

            const outputBox = document.getElementById('output4');
            outputBox.textContent = '프로젝트 생성 중입니다. 잠시 기다려주세요...';
            outputBox.classList.add('visible');
            outputBox.classList.remove('success', 'error');

            try {
                const response = await fetch('/supabase_create_project', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        org_id: orgId,
                        project_name: projectName,
                        db_password: dbPassword,
                        region: region
                    })
                });
                const result = await response.json();

                if (result.success) {
                    outputBox.textContent = result.output || '프로젝트 생성 완료!';
                    outputBox.classList.add('success');
                    outputBox.classList.remove('error');
                    setStatus('프로젝트 생성 완료', 'normal');
                    btn.textContent = '✓ 생성됨';

                    // 프로젝트 목록 새로고침
                    setTimeout(() => fetchFromCLI(), 1000);
                } else {
                    outputBox.textContent = result.error || '프로젝트 생성 실패';
                    outputBox.classList.add('error');
                    outputBox.classList.remove('success');
                    setStatus('프로젝트 생성 실패', 'error');
                    btn.textContent = '프로젝트 생성';
                    btn.disabled = false;
                }
            } catch (error) {
                setStatus('연결 오류', 'error');
                btn.textContent = '프로젝트 생성';
                btn.disabled = false;
                console.error(error);
            }
        }

        async function fetchFromCLI() {
            const btnFetch = document.getElementById('btnFetchCLI');
            btnFetch.disabled = true;
            btnFetch.classList.add('running');
            btnFetch.innerHTML = '<span class="spinner"></span>가져오는 중...';
            setStatus('Supabase CLI에서 프로젝트 목록 가져오는 중...', 'running');

            try {
                const response = await fetch('/supabase_projects', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({})
                });
                const result = await response.json();

                const outputBox = document.getElementById('output4');
                outputBox.textContent = result.output || result.error || '';
                outputBox.classList.add('visible');
                outputBox.classList.remove('success', 'error');

                if (result.success && result.projects) {
                    outputBox.classList.add('success');
                    supabaseProjects = result.projects;

                    // 프로젝트 select 업데이트
                    const select = document.getElementById('supabaseProject');
                    select.innerHTML = '<option value="">-- 프로젝트 선택 --</option>';
                    result.projects.forEach(p => {
                        const status = p.status === 'ACTIVE_HEALTHY' ? '✓' : '⚠';
                        select.innerHTML += `<option value="${p.ref}">${status} ${p.name} (${p.region})</option>`;
                    });

                    setStatus('프로젝트 목록 로드 완료', 'normal');
                    btnFetch.textContent = '✓ 로드됨';
                    btnFetch.classList.remove('running');

                    // 프로젝트 선택 이벤트 등록
                    select.onchange = () => selectProject(select.value);
                } else {
                    outputBox.classList.add('error');
                    setStatus('CLI 오류', 'error');
                    btnFetch.textContent = 'CLI에서 가져오기';
                    btnFetch.disabled = false;
                    btnFetch.classList.remove('running');
                }
            } catch (error) {
                setStatus('연결 오류', 'error');
                btnFetch.textContent = 'CLI에서 가져오기';
                btnFetch.disabled = false;
                btnFetch.classList.remove('running');
                console.error(error);
            }
        }

        async function selectProject(projectRef) {
            if (!projectRef) return;

            const project = supabaseProjects.find(p => p.ref === projectRef);
            if (project) {
                // URL 자동 입력
                document.getElementById('supabaseUrl').value = `https://${project.ref}.supabase.co`;
            }

            // API 키 가져오기
            setStatus('API 키 가져오는 중...', 'running');

            try {
                const response = await fetch('/supabase_api_keys', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ project_ref: projectRef })
                });
                const result = await response.json();

                const outputBox = document.getElementById('output4');

                if (result.success && result.anon_key) {
                    document.getElementById('supabaseAnonKey').value = result.anon_key;
                    outputBox.textContent = `✓ 프로젝트: ${project.name}\\n✓ URL: https://${project.ref}.supabase.co\\n✓ Anon Key 자동 입력됨`;
                    outputBox.classList.remove('error');
                    outputBox.classList.add('success');
                    setStatus('프로젝트 정보 로드 완료', 'normal');
                } else {
                    outputBox.textContent = result.error || 'API 키를 가져올 수 없습니다.';
                    outputBox.classList.remove('success');
                    outputBox.classList.add('error');
                    setStatus('API 키 로드 실패', 'error');
                }
            } catch (error) {
                setStatus('연결 오류', 'error');
                console.error(error);
            }
        }

        async function saveConfig() {
            const supabaseUrl = document.getElementById('supabaseUrl').value.trim();
            const supabaseAnonKey = document.getElementById('supabaseAnonKey').value.trim();
            const botEmail = document.getElementById('botEmail').value.trim();
            const botPassword = document.getElementById('botPassword').value.trim();

            // 유효성 검사
            if (!supabaseUrl || !supabaseAnonKey) {
                alert('Supabase URL과 Anon Key는 필수입니다.');
                return;
            }
            if (!supabaseUrl.includes('.supabase.co')) {
                alert('올바른 Supabase URL을 입력하세요.');
                return;
            }

            const btnSave = document.getElementById('btnSaveConfig');
            btnSave.disabled = true;
            btnSave.classList.add('running');
            btnSave.innerHTML = '<span class="spinner"></span>저장 중...';
            setStatus('설정 파일 생성 중...', 'running');

            try {
                const response = await fetch('/save_config', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        supabase_url: supabaseUrl,
                        supabase_anon_key: supabaseAnonKey,
                        bot_email: botEmail,
                        bot_password: botPassword
                    })
                });
                const result = await response.json();

                const outputBox = document.getElementById('output4');
                outputBox.textContent = result.output || result.error || '완료';
                outputBox.classList.add('visible');
                outputBox.classList.remove('success', 'error');

                if (result.success) {
                    outputBox.classList.add('success');
                    setStatus('설정 저장 완료', 'normal');
                    btnSave.textContent = '✓ 저장됨';
                    btnSave.classList.remove('running');

                    // 폼 숨기기 및 다음 단계 활성화
                    document.getElementById('configForm').classList.remove('visible');
                    document.getElementById('btnConfigForm').style.display = 'none';
                    btnSave.style.display = 'none';

                    completeStep(4);
                    enableStep(5);
                } else {
                    outputBox.classList.add('error');
                    setStatus('오류 발생', 'error');
                    btnSave.textContent = '설정 저장';
                    btnSave.disabled = false;
                    btnSave.classList.remove('running');
                }
            } catch (error) {
                setStatus('연결 오류', 'error');
                btnSave.textContent = '설정 저장';
                btnSave.disabled = false;
                btnSave.classList.remove('running');
                console.error(error);
            }
        }

        async function checkNode(button) {
            const originalText = button.textContent;
            button.disabled = true;
            button.classList.add('running');
            button.innerHTML = '<span class="spinner"></span>확인 중...';
            setStatus('Node.js 확인 중...', 'running');

            try {
                const response = await fetch('/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: 'check_node' })
                });
                const result = await response.json();

                const outputBox = document.getElementById('output3');
                outputBox.textContent = result.output || result.error || '완료';
                outputBox.classList.add('visible');
                outputBox.classList.remove('success', 'error');

                if (result.success) {
                    outputBox.classList.add('success');
                    setStatus('Node.js 확인 완료', 'normal');
                    button.textContent = '✓ Node.js';
                    button.classList.remove('running');

                    // need_restart가 있으면 재시작 안내
                    if (result.need_restart) {
                        setStatus('터미널 재시작 필요', 'running');
                        outputBox.textContent += '\\n\\n⚠️ 터미널(CMD)을 닫고 install.bat을 다시 실행하세요!';
                    } else {
                        // 다른 CLI 설치 버튼 활성화
                        document.getElementById('btnInstallClaude').disabled = false;
                        document.getElementById('btnSupabase').disabled = false;
                        document.getElementById('btnRailway').disabled = false;
                    }
                } else {
                    outputBox.classList.add('error');
                    setStatus('오류 발생', 'error');
                    button.textContent = originalText;
                    button.disabled = false;
                    button.classList.remove('running');
                }
            } catch (error) {
                setStatus('연결 오류', 'error');
                button.textContent = originalText;
                button.disabled = false;
                button.classList.remove('running');
                console.error(error);
            }
        }

        async function checkWithFallback(command, button) {
            const originalText = button.textContent;
            button.disabled = true;
            button.classList.add('running');
            button.innerHTML = '<span class="spinner"></span>확인 중...';
            setStatus(originalText + ' 확인 중...', 'running');

            try {
                const response = await fetch('/run', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ command: command })
                });
                const result = await response.json();

                const outputBox = document.getElementById('output3');
                outputBox.textContent = result.output || result.error || '완료';
                outputBox.classList.add('visible');
                outputBox.classList.remove('success', 'error');

                if (result.success) {
                    outputBox.classList.add('success');
                    setStatus('완료', 'normal');
                    button.textContent = '✓ ' + originalText;
                    button.classList.remove('running');
                } else {
                    outputBox.classList.add('error');
                    setStatus('오류 발생', 'error');
                    button.textContent = originalText;
                    button.disabled = false;
                    button.classList.remove('running');
                }
            } catch (error) {
                setStatus('연결 오류', 'error');
                button.textContent = originalText;
                button.disabled = false;
                button.classList.remove('running');
                console.error(error);
            }
        }
    </script>
</body>
</html>
"""


# 실행할 명령어 정의
COMMANDS = {
    'pip_install': {
        'cmd': ['python', '-m', 'pip', 'install', 'realtime', 'supabase', 'python-dotenv'],
        'desc': 'Python 패키지 설치'
    },
    'check_node': {
        'cmd': ['node', '--version'],
        'desc': 'Node.js 버전 확인',
        'fallback': 'install_node'  # 실패 시 실행할 명령
    },
    'install_node': {
        'cmd': ['winget', 'install', '-e', '--id', 'OpenJS.NodeJS', '--accept-source-agreements', '--accept-package-agreements'],
        'desc': 'Node.js 설치 (winget)'
    },
    'install_claude': {
        'cmd': ['npm', 'install', '-g', '@anthropic-ai/claude-code'],
        'desc': 'Claude CLI 설치'
    },
    'check_supabase': {
        'cmd': ['supabase', '--version'],
        'desc': 'Supabase CLI 버전 확인',
        'fallback': 'install_supabase'
    },
    'install_supabase': {
        'cmd': ['npm', 'install', '-g', 'supabase'],
        'desc': 'Supabase CLI 설치 (npm)'
    },
    'check_railway': {
        'cmd': ['railway', '--version'],
        'desc': 'Railway CLI 버전 확인',
        'fallback': 'install_railway'
    },
    'install_railway': {
        'cmd': ['npm', 'install', '-g', '@railway/cli'],
        'desc': 'Railway CLI 설치 (npm)'
    },
    'run_bot': {
        'cmd': ['python', '../chat_bot/chat.py'],
        'desc': '채팅봇 실행'
    }
}


class InstallerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(HTML_CONTENT.encode('utf-8'))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data.decode('utf-8'))

        if self.path == '/run':
            command_key = data.get('command')
            result = self.execute_command(command_key)
        elif self.path == '/save_config':
            result = self.save_config(data)
        elif self.path == '/supabase_projects':
            result = self.get_supabase_projects()
        elif self.path == '/supabase_api_keys':
            result = self.get_supabase_api_keys(data)
        elif self.path == '/supabase_orgs':
            result = self.get_supabase_orgs()
        elif self.path == '/supabase_create_project':
            result = self.create_supabase_project(data)
        else:
            self.send_response(404)
            self.end_headers()
            return

        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.end_headers()
        self.wfile.write(json.dumps(result, ensure_ascii=False).encode('utf-8'))

    def save_config(self, data):
        """설정 파일 생성 (.env, config.js)"""
        supabase_url = data.get('supabase_url', '')
        supabase_anon_key = data.get('supabase_anon_key', '')
        bot_email = data.get('bot_email', '')
        bot_password = data.get('bot_password', '')

        # 현재 스크립트의 부모 디렉토리 (프로젝트 루트)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)

        output_lines = []

        try:
            # 1. chat_bot/.env 파일 생성
            env_path = os.path.join(project_root, 'chat_bot', '.env')
            env_content = f"""SUPABASE_URL={supabase_url}
SUPABASE_ANON_KEY={supabase_anon_key}

# Bot authentication (for private channel access)
BOT_EMAIL={bot_email}
BOT_PASSWORD={bot_password}
"""
            with open(env_path, 'w', encoding='utf-8') as f:
                f.write(env_content)
            output_lines.append(f"✓ {env_path} 생성 완료")

            # 2. chat_client/config.js 파일 생성
            config_path = os.path.join(project_root, 'chat_client', 'config.js')
            config_content = f"""const SUPABASE_URL = '{supabase_url}';
const SUPABASE_ANON_KEY = '{supabase_anon_key}';
const CHANNEL_NAME = 'chat-room';
"""
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
            output_lines.append(f"✓ {config_path} 생성 완료")

            return {
                'success': True,
                'output': '\n'.join(output_lines)
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'output': '\n'.join(output_lines) + f'\n\n오류: {e}'
            }

    def execute_command(self, command_key):
        if command_key not in COMMANDS:
            return {'success': False, 'error': f'알 수 없는 명령: {command_key}'}

        cmd_info = COMMANDS[command_key]
        cmd = cmd_info['cmd']
        desc = cmd_info['desc']

        print(f"[실행] {desc}: {' '.join(cmd)}")

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300,
                shell=True  # Windows에서 필요
            )

            output = result.stdout
            if result.stderr:
                output += '\n[stderr]\n' + result.stderr

            success = result.returncode == 0
            print(f"[결과] 성공: {success}")

            # 실패 시 fallback 명령 실행
            if not success and 'fallback' in cmd_info:
                fallback_key = cmd_info['fallback']
                fallback_info = COMMANDS.get(fallback_key, {})
                tool_name = desc.replace(' 버전 확인', '').replace(' 확인', '')

                print(f"[Fallback] {command_key} 실패, {fallback_key} 실행")
                output += f"\n\n--- {tool_name}가 설치되어 있지 않습니다. 설치를 시작합니다... ---\n"

                fallback_result = self.execute_command(fallback_key)
                output += fallback_result.get('output', '')

                if fallback_result['success']:
                    # Node.js는 PATH 갱신 필요
                    if command_key == 'check_node':
                        output += f"\n\n✓ {tool_name} 설치 완료! 터미널을 재시작한 후 다시 시도하세요."
                        return {
                            'success': True,
                            'output': output.strip(),
                            'returncode': 0,
                            'need_restart': True
                        }
                    else:
                        output += f"\n\n✓ {tool_name} 설치 완료!"
                        return {
                            'success': True,
                            'output': output.strip(),
                            'returncode': 0
                        }
                else:
                    return {
                        'success': False,
                        'output': output.strip(),
                        'error': fallback_result.get('error', 'Fallback 실패')
                    }

            return {
                'success': success,
                'output': output.strip() if output else '(출력 없음)',
                'returncode': result.returncode
            }
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': '명령 실행 시간 초과 (300초)'}
        except FileNotFoundError as e:
            return {'success': False, 'error': f'명령을 찾을 수 없음: {e}'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_supabase_projects(self):
        """Supabase CLI로 프로젝트 목록 가져오기"""
        print("[실행] Supabase 프로젝트 목록 조회")

        try:
            result = subprocess.run(
                ['supabase', 'projects', 'list', '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                if 'not logged in' in error_msg.lower() or 'login' in error_msg.lower():
                    return {
                        'success': False,
                        'error': 'Supabase CLI 로그인이 필요합니다.\n터미널에서 "supabase login" 실행 후 다시 시도하세요.'
                    }
                return {'success': False, 'error': error_msg}

            # JSON 파싱
            projects = json.loads(result.stdout)
            print(f"[결과] {len(projects)}개 프로젝트 로드")

            return {
                'success': True,
                'projects': projects,
                'output': f'{len(projects)}개 프로젝트 로드됨'
            }

        except json.JSONDecodeError as e:
            return {'success': False, 'error': f'JSON 파싱 오류: {e}'}
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': '시간 초과'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_supabase_api_keys(self, data):
        """Supabase CLI로 API 키 가져오기"""
        project_ref = data.get('project_ref', '')
        if not project_ref:
            return {'success': False, 'error': '프로젝트 ref가 필요합니다.'}

        print(f"[실행] Supabase API 키 조회: {project_ref}")

        try:
            result = subprocess.run(
                ['supabase', 'projects', 'api-keys', '--project-ref', project_ref, '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )

            if result.returncode != 0:
                return {'success': False, 'error': result.stderr or result.stdout}

            # JSON 파싱
            api_keys = json.loads(result.stdout)

            # anon 키 찾기
            anon_key = None
            for key in api_keys:
                if key.get('name') == 'anon' or key.get('id') == 'anon':
                    anon_key = key.get('api_key')
                    break

            if anon_key:
                print(f"[결과] Anon Key 로드 성공")
                return {
                    'success': True,
                    'anon_key': anon_key,
                    'output': 'Anon Key 로드 완료'
                }
            else:
                return {'success': False, 'error': 'Anon Key를 찾을 수 없습니다.'}

        except json.JSONDecodeError as e:
            return {'success': False, 'error': f'JSON 파싱 오류: {e}'}
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': '시간 초과'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_supabase_orgs(self):
        """Supabase CLI로 조직 목록 가져오기"""
        print("[실행] Supabase 조직 목록 조회")

        try:
            result = subprocess.run(
                ['supabase', 'orgs', 'list', '-o', 'json'],
                capture_output=True,
                text=True,
                timeout=30,
                shell=True
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout
                if 'not logged in' in error_msg.lower() or 'login' in error_msg.lower():
                    return {
                        'success': False,
                        'error': 'Supabase CLI 로그인이 필요합니다.\n터미널에서 "supabase login" 실행 후 다시 시도하세요.'
                    }
                return {'success': False, 'error': error_msg}

            orgs = json.loads(result.stdout)
            print(f"[결과] {len(orgs)}개 조직 로드")

            return {
                'success': True,
                'orgs': orgs,
                'output': f'{len(orgs)}개 조직 로드됨'
            }

        except json.JSONDecodeError as e:
            return {'success': False, 'error': f'JSON 파싱 오류: {e}'}
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': '시간 초과'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def create_supabase_project(self, data):
        """Supabase CLI로 프로젝트 생성"""
        org_id = data.get('org_id', '')
        project_name = data.get('project_name', '')
        db_password = data.get('db_password', '')
        region = data.get('region', 'ap-northeast-1')

        if not org_id or not project_name or not db_password:
            return {'success': False, 'error': '필수 정보가 누락되었습니다.'}

        print(f"[실행] Supabase 프로젝트 생성: {project_name}")

        try:
            result = subprocess.run(
                [
                    'supabase', 'projects', 'create', project_name,
                    '--org-id', org_id,
                    '--db-password', db_password,
                    '--region', region
                ],
                capture_output=True,
                text=True,
                timeout=180,  # 프로젝트 생성은 시간이 걸림
                shell=True
            )

            output = result.stdout
            if result.stderr:
                output += '\n' + result.stderr

            if result.returncode == 0:
                print(f"[결과] 프로젝트 생성 성공")
                return {
                    'success': True,
                    'output': f'✓ 프로젝트 "{project_name}" 생성 완료!\n\n{output}'
                }
            else:
                return {
                    'success': False,
                    'error': output or '프로젝트 생성 실패'
                }

        except subprocess.TimeoutExpired:
            return {'success': False, 'error': '프로젝트 생성 시간 초과 (3분)'}
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def log_message(self, format, *args):
        print(f"[Server] {args[0]}")


def open_browser():
    webbrowser.open(f'http://localhost:{PORT}')


if __name__ == '__main__':
    print(f"설치 마법사 서버 시작: http://localhost:{PORT}")

    # 브라우저 자동 오픈 (별도 스레드)
    threading.Timer(1.0, open_browser).start()

    with socketserver.TCPServer(("", PORT), InstallerHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n서버 종료")
