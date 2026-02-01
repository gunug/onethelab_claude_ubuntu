"""
Google OAuth 2.0 인증 모듈
"""
import os
import secrets
import urllib.parse
from typing import Optional, Dict, Any, List
import aiohttp


class GoogleOAuth:
    """Google OAuth 2.0 인증 처리"""

    AUTHORIZATION_URL = "https://accounts.google.com/o/oauth2/v2/auth"
    TOKEN_URL = "https://oauth2.googleapis.com/token"
    USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        allowed_emails: Optional[List[str]] = None
    ):
        """
        Args:
            client_id: Google OAuth 클라이언트 ID
            client_secret: Google OAuth 클라이언트 시크릿
            redirect_uri: OAuth 콜백 URL
            allowed_emails: 허용된 이메일 목록 (None이면 모든 이메일 허용)
        """
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.allowed_emails = allowed_emails or []

        # CSRF 방지를 위한 state 토큰 저장
        self._pending_states: Dict[str, float] = {}

    def get_authorization_url(self) -> tuple[str, str]:
        """
        Google OAuth 인증 URL 생성

        Returns:
            (authorization_url, state) 튜플
        """
        state = secrets.token_urlsafe(32)

        # state 저장 (5분 후 만료)
        import time
        self._pending_states[state] = time.time() + 300
        self._cleanup_expired_states()

        params = {
            'client_id': self.client_id,
            'redirect_uri': self.redirect_uri,
            'response_type': 'code',
            'scope': 'openid email profile',
            'state': state,
            'access_type': 'online',
            'prompt': 'select_account'
        }

        url = f"{self.AUTHORIZATION_URL}?{urllib.parse.urlencode(params)}"
        return url, state

    def verify_state(self, state: str) -> bool:
        """state 토큰 검증"""
        import time
        self._cleanup_expired_states()

        if state not in self._pending_states:
            return False

        # 사용된 state 삭제 (재사용 방지)
        del self._pending_states[state]
        return True

    def _cleanup_expired_states(self):
        """만료된 state 토큰 정리"""
        import time
        now = time.time()
        expired = [s for s, exp in self._pending_states.items() if exp < now]
        for s in expired:
            del self._pending_states[s]

    async def exchange_code(self, code: str) -> Optional[Dict[str, Any]]:
        """
        인증 코드를 액세스 토큰으로 교환

        Args:
            code: Google에서 받은 인증 코드

        Returns:
            토큰 정보 또는 None (실패 시)
        """
        data = {
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'code': code,
            'grant_type': 'authorization_code',
            'redirect_uri': self.redirect_uri
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.TOKEN_URL, data=data) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        print(f"[OAuth] 토큰 교환 실패: {resp.status} - {error_text}")
                        return None
                    return await resp.json()
        except Exception as e:
            print(f"[OAuth] 토큰 교환 예외: {e}")
            return None

    async def get_user_info(self, access_token: str) -> Optional[Dict[str, Any]]:
        """
        액세스 토큰으로 사용자 정보 조회

        Args:
            access_token: Google 액세스 토큰

        Returns:
            사용자 정보 또는 None (실패 시)
        """
        headers = {'Authorization': f'Bearer {access_token}'}

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.USERINFO_URL, headers=headers) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        print(f"[OAuth] 사용자 정보 조회 실패: {resp.status} - {error_text}")
                        return None
                    return await resp.json()
        except Exception as e:
            print(f"[OAuth] 사용자 정보 조회 예외: {e}")
            return None

    def is_email_allowed(self, email: str) -> bool:
        """이메일이 허용 목록에 있는지 확인"""
        if not self.allowed_emails:
            # 허용 목록이 비어있으면 모든 이메일 허용
            return True
        return email.lower() in [e.lower() for e in self.allowed_emails]

    async def authenticate(self, code: str) -> Optional[Dict[str, Any]]:
        """
        전체 인증 플로우 수행

        Args:
            code: Google 인증 코드

        Returns:
            인증된 사용자 정보 또는 None
        """
        # 1. 코드를 토큰으로 교환
        token_data = await self.exchange_code(code)
        if not token_data:
            return None

        access_token = token_data.get('access_token')
        if not access_token:
            print("[OAuth] 액세스 토큰 없음")
            return None

        # 2. 사용자 정보 조회
        user_info = await self.get_user_info(access_token)
        if not user_info:
            return None

        email = user_info.get('email', '')

        # 3. 이메일 허용 여부 확인
        if not self.is_email_allowed(email):
            print(f"[OAuth] 허용되지 않은 이메일: {email}")
            return None

        return {
            'email': email,
            'name': user_info.get('name', ''),
            'picture': user_info.get('picture', ''),
            'id': user_info.get('id', '')
        }


def create_oauth_from_env() -> Optional[GoogleOAuth]:
    """
    환경 변수에서 OAuth 설정을 읽어 GoogleOAuth 인스턴스 생성

    환경 변수:
        GOOGLE_CLIENT_ID: Google OAuth 클라이언트 ID
        GOOGLE_CLIENT_SECRET: Google OAuth 클라이언트 시크릿
        OAUTH_REDIRECT_URI: OAuth 콜백 URL (선택, 기본값은 동적 생성)
        ALLOWED_EMAILS: 허용 이메일 목록 (쉼표 구분)

    Returns:
        GoogleOAuth 인스턴스 또는 None (필수 환경 변수 없는 경우)
    """
    client_id = os.environ.get('GOOGLE_CLIENT_ID')
    client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')

    if not client_id or not client_secret:
        return None

    # 허용 이메일 목록 파싱
    allowed_emails_str = os.environ.get('ALLOWED_EMAILS', '')
    allowed_emails = [
        e.strip() for e in allowed_emails_str.split(',')
        if e.strip()
    ]

    # redirect_uri는 나중에 요청 시 동적으로 설정
    return GoogleOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri='',  # 동적 설정
        allowed_emails=allowed_emails
    )
