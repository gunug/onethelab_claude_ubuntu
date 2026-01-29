#!/usr/bin/env python3
"""
OTP 설정 스크립트
Google Authenticator 등록을 위한 비밀키 및 QR 코드 생성
"""

import pyotp
import qrcode
import os
from pathlib import Path


def generate_secret():
    """랜덤 비밀키 생성"""
    return pyotp.random_base32()


def generate_qr_code(secret: str, name: str = "ChatBot", issuer: str = "OneTheLab"):
    """QR 코드 생성"""
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=name, issuer_name=issuer)

    # QR 코드 이미지 생성
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(uri)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img, uri


def main():
    print("=" * 50)
    print("  OTP 설정 도구")
    print("=" * 50)
    print()

    # 새 비밀키 생성
    secret = generate_secret()

    print(f"1. 비밀키가 생성되었습니다:")
    print(f"   {secret}")
    print()

    # .env 파일 업데이트 안내
    env_path = Path(__file__).parent / ".env"
    print(f"2. 다음 내용을 .env 파일에 추가하세요:")
    print(f"   TOTP_SECRET_KEY={secret}")
    print()

    # QR 코드 생성
    try:
        img, uri = generate_qr_code(secret)
        qr_path = Path(__file__).parent / "otp_qrcode.png"
        img.save(qr_path)
        print(f"3. QR 코드가 생성되었습니다:")
        print(f"   {qr_path}")
        print()
        print(f"4. Google Authenticator 앱에서 QR 코드를 스캔하세요.")
        print()
    except ImportError:
        print("3. QR 코드 생성 실패 (qrcode 라이브러리 필요)")
        print(f"   pip install qrcode[pil]")
        print()
        print(f"   수동 등록 URI:")
        totp = pyotp.TOTP(secret)
        uri = totp.provisioning_uri(name="ChatBot", issuer_name="OneTheLab")
        print(f"   {uri}")
        print()

    # 테스트
    print("5. 테스트:")
    totp = pyotp.TOTP(secret)
    current_code = totp.now()
    print(f"   현재 OTP 코드: {current_code}")
    print()

    # 검증 테스트
    test_input = input("   앱에 표시된 코드를 입력하여 테스트하세요 (Enter로 건너뛰기): ").strip()
    if test_input:
        if totp.verify(test_input, valid_window=1):
            print("   ✓ 인증 성공!")
        else:
            print("   ✗ 인증 실패. 코드를 확인하세요.")

    print()
    print("=" * 50)
    print("  설정 완료!")
    print("=" * 50)
    print()
    print("주의사항:")
    print("- 비밀키는 안전하게 보관하세요.")
    print("- QR 코드 이미지(otp_qrcode.png)는 등록 후 삭제하는 것이 좋습니다.")
    print("- .env 파일을 Git에 커밋하지 마세요.")


if __name__ == "__main__":
    main()
