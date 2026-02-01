"""
메모리 기반 세션 관리
"""
import secrets
import time
from typing import Optional, Dict, Any


class SessionManager:
    """간단한 메모리 기반 세션 관리자"""

    def __init__(self, session_timeout: int = 86400):
        """
        Args:
            session_timeout: 세션 만료 시간 (초), 기본 24시간
        """
        self._sessions: Dict[str, Dict[str, Any]] = {}
        self._session_timeout = session_timeout

    def create_session(self, user_data: Dict[str, Any]) -> str:
        """새 세션 생성"""
        session_id = secrets.token_urlsafe(32)
        self._sessions[session_id] = {
            'user': user_data,
            'created_at': time.time(),
            'last_accessed': time.time()
        }
        self._cleanup_expired()
        return session_id

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """세션 조회 (존재하고 유효한 경우 사용자 데이터 반환)"""
        if not session_id:
            return None

        session = self._sessions.get(session_id)
        if not session:
            return None

        # 만료 체크
        if time.time() - session['last_accessed'] > self._session_timeout:
            del self._sessions[session_id]
            return None

        # 마지막 접근 시간 갱신
        session['last_accessed'] = time.time()
        return session['user']

    def delete_session(self, session_id: str) -> bool:
        """세션 삭제"""
        if session_id in self._sessions:
            del self._sessions[session_id]
            return True
        return False

    def _cleanup_expired(self):
        """만료된 세션 정리"""
        now = time.time()
        expired = [
            sid for sid, session in self._sessions.items()
            if now - session['last_accessed'] > self._session_timeout
        ]
        for sid in expired:
            del self._sessions[sid]

    def get_session_count(self) -> int:
        """활성 세션 수 반환"""
        self._cleanup_expired()
        return len(self._sessions)
