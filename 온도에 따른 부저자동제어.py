# 라즈베리파이의 GPIO 핀을 제어하기 위한 라이브러리입니다.
import RPi.GPIO as GPIO

# 시간 관련 기능을 사용하기 위한 라이브러리입니다.
import time 

# 부저(Buzzer)가 연결된 핀 번호를 설정합니다.
# 여기서는 GPIO 18번 핀을 사용합니다.
buzzer_pin = 18

# GPIO 경고 메시지를 끕니다. (중복 실행 시 나오는 경고를 방지)
GPIO.setwarnings(False)

# GPIO 핀 번호를 BCM 모드로 설정합니다. (GPIO 숫자 기준으로 사용)
GPIO.setmode(GPIO.BCM)

# 부저 핀을 출력 모드로 설정합니다.
GPIO.setup(buzzer_pin, GPIO.OUT)


# 온도에 따라 부저를 울리는 함수입니다.
def control_buzzer(temp):
    # 만약 온도가 20도 이상이면 부저를 울립니다.
    if temp >= 20:
        # 간단한 멜로디용 주파수 리스트입니다. (도, 레, 미, 파, 솔, 라, 시, 도)
        notes = [262, 294, 330, 349, 392, 440, 493, 523]

        # PWM(펄스 폭 변조)을 사용해서 소리를 냅니다. 초기 주파수는 100Hz
        buzzer = GPIO.PWM(buzzer_pin, 100)

        # 부저를 50% 세기로 시작합니다.
        buzzer.start(50)

        # 위에서 지정한 음들을 하나씩 재생합니다.
        for f in notes:
            buzzer.ChangeFrequency(f)  # 주파수를 변경해서 음을 바꿉니다.
            time.sleep(0.3)            # 0.3초 동안 소리를 냅니다.

        # 멜로디가 끝나면 부저를 멈춥니다.
        buzzer.stop()

    else:
        # 온도가 20도 미만이면 부저를 울리지 않고 꺼둡니다.(테스트를 위해 기준을 20도로 설정)
        GPIO.output(buzzer_pin, 0)
