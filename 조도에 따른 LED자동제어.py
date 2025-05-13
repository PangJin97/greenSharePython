# 라즈베리파이의 GPIO 핀을 제어하기 위한 라이브러리를 불러옵니다.
import RPi.GPIO as GPIO

# 시간 지연을 위한 라이브러리입니다. (ex. 1초 멈추기)
import time

# 사용할 GPIO 핀 번호를 설정합니다.
# 여기서는 GPIO 4번 핀에 LED를 연결했다고 가정합니다.
led_pin = 4

# GPIO 관련 경고 메시지를 비활성화합니다. (코드 반복 실행 시 깔끔하게 하기 위해 사용)
GPIO.setwarnings(False)

# GPIO 핀 번호를 설정하는 모드입니다.
# BCM 모드는 'GPIO 숫자 그대로' 사용하는 방식입니다.
GPIO.setmode(GPIO.BCM)

# 지정한 핀을 '출력 모드'로 설정합니다.
GPIO.setup(led_pin, GPIO.OUT)

# for문을 이용해 LED를 10번 깜빡이게 합니다.
for i in range(10):
    GPIO.output(led_pin, 1)  # LED 켜기 (HIGH 신호)
    time.sleep(1)            # 1초 동안 켠 상태 유지
    GPIO.output(led_pin, 0)  # LED 끄기 (LOW 신호)
    time.sleep(1)            # 1초 동안 끈 상태 유지

# 모든 작업이 끝난 후, 사용한 GPIO 핀을 정리합니다.
# 다른 프로그램이 GPIO를 사용할 수 있도록 초기화해주는 역할입니다.
GPIO.cleanup()

#조도에 따른 led 컨트롤
def controlLED(ldr_value):
  #4번 GPIO에 LED 전선 연결 됨
  led_pin=4
  GPIO.setwarnings(False)

  #앞으로 핀 번호는 BCM 방식으로 지정
  GPIO.setmode(GPIO.BCM)

  # 4번핀(LED가 연결된 핀)을 전류를 방출!!
  #GPIO.OUT은 전류를 내보내겠다는 것
  GPIO.setup(led_pin, GPIO.OUT)

  #조도에 따라 LED 작동
  #테스트를 위해 50이상이면 LED자동으로 켜짐
  if(ldr_value >= 50):
    GPIO.output(led_pin,1)
    #1은 전류 흐름
  else:
    GPIO.output(led_pin,0)
    #0은 전류가 흐르지 않음 
  GPIO.cleanup()
  