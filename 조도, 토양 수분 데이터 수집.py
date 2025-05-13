# ─────────────────────────────
# [라즈베리파이 통합 센서 측정 코드]
# - 토양 수분 센서 + LDR 조도 센서
# - MCP3008 아날로그 → 디지털 변환기 사용
# ─────────────────────────────

import spidev    # SPI 통신을 위한 모듈
import time      # 시간 지연(쉬는 시간)을 주기 위한 모듈

# ───── 설정값 ─────
delay = 1 # 측정 주기: 1초 

# MCP3008 채널 설정
ldr_channel = 0     # LDR 조도 센서 → 채널 0번
soil_channel = 1    # 토양 수분 센서 → 채널 1번

# SPI 통신 초기화
spi = spidev.SpiDev()      # SPI 객체 생성
spi.open(0, 0)             # 버스 0, 디바이스 0 사용
spi.max_speed_hz = 100000  # 통신 속도 설정

# MCP3008에서 아날로그 값을 읽는 함수
def readadc(channel):
    # 채널 번호가 0~7 범위를 벗어나면 -1 반환
    if channel > 7 or channel < 0:
        return -1

    # MCP3008에 읽기 요청 → 3바이트 전송
    r = spi.xfer2([1, (8 + channel) << 4, 0])

    # 받은 응답(r)에서 실제 값을 계산 (0~1023 범위)
    result = ((r[1] & 3) << 8) + r[2]
    return result

# ───── 메인 루프 ─────
while True:
    # 조도 센서 값 읽기
    ldr_value = readadc(ldr_channel)  # 밝기 값 (높을수록 밝음)

    # 토양 수분 값 읽기
    soil_value = readadc(soil_channel)  # 높을수록 건조, 낮을수록 촉촉

    # 결과 출력
    print("===========================================")
    print(f"조도(LDR) 값: {ldr_value} (0~1023, 높을수록 밝음)")
    print(f"토양 수분 값: {soil_value} (0~1023, 높을수록 건조)")
    print("===========================================\n")

    # 일정 시간 기다리기
    time.sleep(delay)  #테스트를 위해 1초 마다 값을 보여줌

#항목설명
#readadc()	센서에서 값을 읽는 함수. 0~1023 사이 숫자를 반환해요.
#ldr_value	**조도(빛의 밝기)**를 나타내요. 높을수록 더 밝은 상태예요.
#soil_value	토양의 수분량을 나타내요. 값이 낮을수록 흙이 촉촉해요.