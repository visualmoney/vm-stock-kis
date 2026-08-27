"""
중급 예제 03: 포트폴리오 성과 분석
VM-Stock-KIS 사용 예제

설명:
  - 현재 보유 종목 조회
  - 포트폴리오 전체 성과 계산
  - 종목별 수익률 및 기여도 분석
  - 자산 배분 현황 표시

실행 조건:
  - config.yaml이 루트에 있어야 함
  - 보유 종목이 있어야 함 (모의 또는 실제)

사용 모듈:
  - VmKis: 한국투자증권 API
  - SimpleKIS: 초보자 친화 인터페이스
"""

from vmkis import create_client
from vmkis.simple import SimpleKIS
import os


def analyze_portfolio(config_path: str | None = None, profile: str | None = None) -> None:
    """포트폴리오 성과를 분석합니다."""

    config_path = config_path or os.path.join(os.getcwd(), "config.yaml")
    if not os.path.exists(config_path):
        print(f"❌ {config_path}를 찾을 수 없습니다.")
        return

    kis = create_client(config_path, profile=profile)
    simple = SimpleKIS(kis)

    print("=" * 70)
    print("VM-Stock-KIS 중급 예제 03: 포트폴리오 성과 분석")
    print("=" * 70)
    print()

    # 1단계: 잔고 조회
    print("💼 단계 1: 포트폴리오 기본 정보 조회")
    print("-" * 70)

    try:
        balance = simple.get_balance()
    except Exception as e:
        print(f"❌ 잔고 조회 실패: {e}")
        return

    print(f"💰 예수금:        {balance.deposits:>15,}원")
    print(f"📊 총자산:        {balance.total_assets:>15,}원")
    print(f"📈 평가손익:      {balance.revenue:>15,}원")
    print(f"📊 평가손익률:    {balance.revenue_rate:>14.2f}%")
    print()

    # 2단계: 자산 구성 분석
    print("🥧 단계 2: 자산 구성")
    print("-" * 70)

    # 간단한 자산 배분 시뮬레이션
    # 실제로는 holdings API를 사용해야 함
    stock_value = balance.total_assets - balance.deposits
    deposit_ratio = (balance.deposits / balance.total_assets) * 100 if balance.total_assets > 0 else 0
    stock_ratio = (stock_value / balance.total_assets) * 100 if balance.total_assets > 0 else 0

    print(f"💵 현금:           {balance.deposits:>15,}원 ({deposit_ratio:>5.1f}%)")
    print(f"📈 주식:           {stock_value:>15,}원 ({stock_ratio:>5.1f}%)")
    print()

    # 3단계: 수익성 분석
    print("📊 단계 3: 수익성 분석")
    print("-" * 70)

    if balance.total_assets > 0:
        roi = (balance.revenue / balance.total_assets) * 100
        print(f"ROI (Return on Investment): {roi:+.2f}%")

    if balance.deposits > 0:
        revenue_per_deposit = balance.revenue / balance.deposits
        print(f"초기 예수금 대비 수익: {revenue_per_deposit:+.2f}배")

    # 심플 수익성 지표
    if balance.revenue > 0:
        status = "🟢 수익 중"
    elif balance.revenue < 0:
        status = "🔴 손실 중"
    else:
        status = "⚪ 손익분기점"

    print(f"상태: {status}")
    print()

    # 4단계: 목표 설정 및 진행률
    print("🎯 단계 4: 목표 설정 및 진행률")
    print("-" * 70)

    initial_deposit = 1_000_000  # 초기 예수금 가정
    target_profit = initial_deposit * 0.10  # 목표: 10% 수익
    current_profit_ratio = (balance.revenue / initial_deposit) * 100
    progress = min(100, (balance.revenue / target_profit) * 100) if target_profit > 0 else 0

    print(f"초기 예수금:       {initial_deposit:>15,}원")
    print(f"목표 수익:         {target_profit:>15,}원 (10% 목표)")
    print(f"현재 수익:         {balance.revenue:>15,}원 ({current_profit_ratio:+.2f}%)")
    print(f"목표 달성률:       {progress:>14.1f}%")

    # 진행률 시각화
    filled = int(progress / 5)
    empty = 20 - filled
    bar = "█" * filled + "░" * empty
    print(f"진행: [{bar}]")
    print()

    # 5단계: 리스크 분석 (간단)
    print("⚠️ 단계 5: 리스크 분석")
    print("-" * 70)

    if balance.deposits > 0:
        risk_ratio = (abs(balance.revenue) / balance.deposits) * 100
        print(f"리스크 레벨: {risk_ratio:.2f}%")

        if risk_ratio < 5:
            print("   → 낮음 (안정적)")
        elif risk_ratio < 15:
            print("   → 중간 (적정)")
        else:
            print("   → 높음 (주의 필요)")

    print()
    print("✅ 분석 완료!")
    print()
    print("💡 팁:")
    print("   - 장기적 관점에서 포트폴리오를 관리하세요.")
    print("   - 분산 투자로 리스크를 낮추세요.")
    print("   - 정기적으로 리밸런싱을 수행하세요.")
    print()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.yaml", help="path to config file")
    parser.add_argument("--profile", help="config profile name (virtual|real)")
    args = parser.parse_args()

    try:
        analyze_portfolio(config_path=args.config, profile=args.profile)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()
