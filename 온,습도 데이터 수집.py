# 필요한 라이브러리를 불러옵니다.
import board           # 라즈베리파이의 핀 번호를 쉽게 다룰 수 있게 해주는 라이브러리입니다.
import adafruit_dht    # DHT22 온습도 센서를 사용하기 위한 라이브러리입니다.
import time            # 시간 관련 기능을 사용하기 위한 라이브러리입니다. (예: 잠시 멈추기)

# DHT22 센서를 사용할 핀을 지정하고, 센서 객체를 만듭니다.
# 여기서는 라즈베리파이의 D16번 핀(GPIO 23번)을 사용합니다.
sensor = adafruit_dht.DHT22(board.D16)

# 계속 반복해서 온도와 습도를 측정하고 출력합니다.
while True:  # 무한 반복문: 계속해서 센서를 확인합니다.
    try:
        # 센서로부터 현재 온도를 읽어옵니다.
        temperature = sensor.temperature

        # 센서로부터 현재 습도를 읽어옵니다.
        humidity = sensor.humidity

        # 읽어온 온도와 습도를 화면에 보기 좋게 출력합니다.
        # 예: Temp: 24.3C | Humidity: 55.1%
        print(f"Temp: {temperature:.1f}C | Humidity: {humidity:.1f}%")

    except Exception as e:
        # 센서를 읽는 도중 오류가 생기면, 오류 메시지를 출력합니다.
        # 예를 들어 센서가 연결되지 않았거나, 일시적인 오류가 있을 때입니다.
        print("e:", e)

    # 2초 동안 기다린 후 다시 측정을 시작합니다.
    # 센서를 너무 자주 읽으면 오작동할 수 있어서, 잠시 쉬는 거예요.
    time.sleep(2)
