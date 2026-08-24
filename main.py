import os
import requests


def calculate_target_price(
    current_stock_price: float,
    current_index: float,
    target_index: float,
    beta: float = 1.1,
) -> float:
    """선물/옵션 목표 지수를 기반으로 개별 주식의 목표 가격을 산출합니다."""
    index_change_rate = (target_index - current_index) / current_index
    stock_change_rate = index_change_rate * beta
    target_stock_price = current_stock_price * (1 + stock_change_rate)

    return round(target_stock_price, -2)


def send_telegram_message(token: str, chat_id: str, message: str) -> None:
    """산출된 분석 결과를 텔레그램 메시지로 전송합니다."""
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("텔레그램 메시지 전송 성공!")
        else:
            print(f"전송 실패 (상태 코드: {response.status_code})")
    except Exception as e:
        print(f"텔레그램 전송 중 오류 발생: {e}")


if __name__ == "__main__":
    # GitHub Secrets에서 보안 정보 가져오기
    TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
    TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        raise ValueError(
            "텔레그램 토큰 또는 Chat ID 환경변수가 설정되지 않았습니다."
        )

    # 시세 데이터 (실시간 API 미연동 시 설정 데이터 기준)
    samsung_price = 256000
    kospi200_current = 1054.01
    target_upper_index = 1051.65
    target_lower_index = 1051.60

    upper_price = calculate_target_price(
        samsung_price, kospi200_current, target_upper_index
    )
    lower_price = calculate_target_price(
        samsung_price, kospi200_current, target_lower_index
    )

    msg = f"""📊 *삼성전자 파생 수급 기반 스윙 목표가*

• *삼성전자 현재가*: {samsung_price:,} 원
• *KOSPI200 현재지수*: {kospi200_current:.2f}

----------------------------------
🎯 *상단 목표가 (상단목표 행사가)*: `{upper_price:,}` 원
🛡️ *하단 지지선 (야간선물)*: `{lower_price:,}` 원
----------------------------------
💡 *대응 전략*
- 상단 도달 시 분할 익절 검토
- 하단 눌림 발생 시 신규/추가 매수 검토
"""

    send_telegram_message(TELEGRAM_TOKEN, TELEGRAM_CHAT_ID, msg)
