# 필요한 라이브러리 가져오기
from flask import Flask, request, jsonify
import threading  # 모니터링 루프를 백그라운드에서 실행하기 위해
import time        # 주기적으로 센서 데이터를 수집하기 위해
import pymysql     # MySQL에 접속하기 위해
import spidev      # SPI 통신을 통해 ADC 데이터 읽기
import RPi.GPIO as GPIO  # GPIO 제어
import board       # DHT 센서 핀 설정
import adafruit_dht  # 온습도 센서 라이브러리

# Flask 서버 시작
app = Flask(__name__)

# GPIO 핀 번호 설정
LED_PIN = 4          # LED 핀
BUZZER_PIN = 18      # 부저 핀
LDR_CHANNEL = 0      # 조도 센서 채널 (ADC)
SOIL_CHANNEL = 1     # 토양 수분 센서 채널 (ADC)
DHT_GPIO = board.D16 # 온습도 센서 핀

# DB 서버 IP 목록 (데이터를 여러 서버에 저장 가능)
IP_LIST = ['192.168.30.166', '192.168.30.110', '192.168.30.70', '192.168.30.91']

# GPIO 초기화
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# 센서 초기화
DHT_SENSOR = adafruit_dht.DHT22(DHT_GPIO)
spi = spidev.SpiDev()
spi.open(0, 0)  # SPI 버스 열기
spi.max_speed_hz = 100000  # SPI 통신 속도

# 최근 측정된 센서 값 저장할 딕셔너리
sensor_data = {
    "temp": None,
    "humidity": None,
    "light": None,
    "soil": None
}

# 현재 선택된 작물 ID (기본값 1)
CURRENT_CROP_ID = 1

# 온습도 센서 값 읽기 함수
def read_dht():
    try:
        return DHT_SENSOR.temperature, DHT_SENSOR.humidity
    except Exception as e:
        print("DHT 센서 오류:", e)
        return None, None

# 아날로그 센서 값 읽기 함수 (조도, 토양 등)
def read_adc(channel):
    r = spi.xfer2([1, (8 + channel) << 4, 0])
    return ((r[1] & 3) << 8) + r[2]

# 토양 센서 값(ADC)을 퍼센트로 변환하는 함수
def convert_soil_to_percent(raw_value):
    return round(100 - (raw_value / 1023.0 * 100), 2)

# 작물의 기준값(온도 범위, 조도 범위)을 DB에서 가져오는 함수
# 가져오는 컬럼: TEMP_MIN, TEMP_MAX, ADC_MIN, ADC_MAX
# 이 값들은 작물별로 설정된 최적 환경값이며, 자동 제어나 수동 판단 시 기준이 됨
def get_thresholds(crop_id):
    conn = pymysql.connect(host='192.168.30.166', user='team4_user', password='mariadb', db='team4')
    cur = conn.cursor()
    cur.execute("SELECT TEMP_MIN, TEMP_MAX, ADC_MIN, ADC_MAX FROM CROP_STANDARDS WHERE ID = %s", (crop_id,))
    result = cur.fetchone()
    conn.close()
    return result

# 센서 데이터를 각 DB 서버에 저장
def send_data(ip, temp, humidity, light, soil):
    try:
        conn = pymysql.connect(host=ip, user='team4_user', password='mariadb', db='team4')
        cur = conn.cursor()
        cur.execute("INSERT INTO ENVIRONMENT (TEMPERATURE, HUMIDITY, ILLUMINANCE, SOIL_MOISTURE) VALUES (%s, %s, %s, %s)",
                    (temp, humidity, light, soil))
        conn.commit()
        conn.close()
        print(f"[{ip}] 데이터 저장 성공")
    except Exception as e:
        print(f"[{ip}] DB 저장 실패:", e)

# 백그라운드에서 실행되는 센서 모니터링 루프
# 자동제어도 이 루프 안에서 실행됨

def monitoring_loop():
    global CURRENT_CROP_ID
    while True:
        temp, humidity = read_dht()
        light = read_adc(LDR_CHANNEL)
        soil_raw = read_adc(SOIL_CHANNEL)
        soil_percent = convert_soil_to_percent(soil_raw)

        if temp is not None and humidity is not None:
            temp_min, temp_max, adc_min, adc_max = get_thresholds(CURRENT_CROP_ID)

            print(f"[자동제어] CropID {CURRENT_CROP_ID}: temp({temp_min}-{temp_max}), light({adc_min}-{adc_max})")
            print(f"[센서 데이터] 온도 {temp}도 | 습도 {humidity}% | 조도 {light} | 토양 {soil_percent}%")

            # 조도에 따라 자동 LED 제어
            GPIO.output(LED_PIN, GPIO.HIGH if light < adc_min else GPIO.LOW)

            # 온도가 기준보다 벗어나면 부저 울림
            margin = 3  # 작물 보호를 위해 기준 온도에서 ±3도 벗어날 경우 알림.
            if temp < (temp_min - margin) or temp > (temp_max + margin):
                buzzer = GPIO.PWM(BUZZER_PIN, 100)
                buzzer.start(50)
                for note in [262, 294, 330, 349, 392]:
                    buzzer.ChangeFrequency(note)
                    time.sleep(0.2)
                buzzer.stop()
            else:
                GPIO.output(BUZZER_PIN, 0)

            # 측정값 업데이트
            sensor_data.update({
                "temp": temp,
                "humidity": humidity,
                "light": light,
                "soil": soil_percent
            })

            # 각 DB 서버에 저장
            for ip in IP_LIST:
                send_data(ip, temp, humidity, light, soil_percent)
                time.sleep(1)

        time.sleep(10)  # 10초마다 측정

# 기본 홈 페이지
@app.route("/")
def home():
    return "Flask + 센서 모니터링 서버 작동 중!"

# 현재 센서 데이터 조회
@app.route("/sensor", methods=["GET"])
def get_sensor():
    global CURRENT_CROP_ID
    crop_id = request.args.get("cropId", type=int)
    if crop_id:
        CURRENT_CROP_ID = crop_id
        print(f"[센서 요청] CropID 변경됨: {CURRENT_CROP_ID}")
    return jsonify(sensor_data)

# 수동으로 LED 제어 요청 처리
@app.route("/led", methods=["POST"])
def led_control():
    global CURRENT_CROP_ID
    data = request.get_json()

    if not data:
        return jsonify({"error": "요청 데이터가 없습니다."}), 400

    state = data.get("state")
    crop_id = data.get("cropId")

    if not state or state not in ["on", "off"]:
        return jsonify({"error": "state 값은 'on' 또는 'off'여야 합니다."}), 400

    if not crop_id:
        return jsonify({"error": "cropId가 필요합니다."}), 400

    CURRENT_CROP_ID = int(crop_id)
    print(f"[LED 제어] CropID 변경됨: {CURRENT_CROP_ID}")

    GPIO.output(LED_PIN, GPIO.HIGH if state == "on" else GPIO.LOW)

    return jsonify({"result": f"LED {state} 성공"})

# cropId 기준으로 전체 수동 제어 요청 처리
@app.route("/control", methods=["POST"])
def control_device():
    global CURRENT_CROP_ID
    data = request.get_json()

    if not data:
        return jsonify({"error": "요청 데이터가 없습니다."}), 400

    crop_id = data.get("cropId")

    if not crop_id:
        return jsonify({"error": "cropId가 필요합니다."}), 400

    CURRENT_CROP_ID = int(crop_id)
    print(f"[수동 제어] CropID 변경됨: {CURRENT_CROP_ID}")

    temp_min, temp_max, adc_min, adc_max = get_thresholds(CURRENT_CROP_ID)
    temp = sensor_data["temp"]
    light = sensor_data["light"]

    if temp is None or light is None:
        return jsonify({"error": "센서 데이터가 없습니다."}), 400

    GPIO.output(LED_PIN, GPIO.HIGH if light < adc_min else GPIO.LOW)

    margin = 10  # 하드코딩된 온도 경고 기준. ±10도 이상 벗어나면 부저 울림.
    if temp < (temp_min - margin) or temp > (temp_max + margin):
        buzzer = GPIO.PWM(BUZZER_PIN, 100)
        buzzer.start(50)
        for note in [262, 294, 330, 349, 392]:
            buzzer.ChangeFrequency(note)
            time.sleep(0.2)
        buzzer.stop()
    else:
        GPIO.output(BUZZER_PIN, 0)

    return jsonify({"result": "수동 제어 완료"})

# 서버 실행
if __name__ == "__main__":
    thread = threading.Thread(target=monitoring_loop, daemon=True)  # 센서 백그라운드 실행
    thread.start()
    app.run(host="0.0.0.0", port=5000)  # 외부에서도 접근 가능하도록 설정
