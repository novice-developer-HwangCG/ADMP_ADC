import machine
import time

adc = machine.ADC(26)   # ADC 핀 (GP26: ADC0)

# 샘플링 주파수 설정
sampling_rate = 128000  # 128kHz
sampling_interval = 1 / sampling_rate  # 샘플링 간격
sample_count = 0  # 1초 동안 샘플링한 데이터 개수

# 타임스탬프 포맷팅 함수
def get_timestamp():
    t = time.localtime()  # 현재 시간 가져오기
    milliseconds = time.ticks_ms() % 1000  # 밀리초 계산
    return "{:02}:{:02}:{:02}.{:03}".format(t[3], t[4], t[5], milliseconds)

# 1초 동안 샘플링을 시작합니다.
start_time = time.ticks_us()  # 시작 시간 (마이크로초)
elapsed_time = 0

while elapsed_time < 1000000:  # 1초 동안 실행 (1000000 마이크로초 = 1초)
    adc_value = adc.read_u16()  # ADC 값 읽기 (0~65535)
    timestamp = get_timestamp()  # 타임스탬프 가져오기
    # print(f"{timestamp} -> {adc_value}")  # 타임스탬프와 ADC 값 출력
    
    sample_count += 1  # 샘플 카운트 증가
    
    time.sleep_us(int(sampling_interval * 1e6))  # 샘플링 주기 동안 마이크로초 단위로 대기

    elapsed_time = time.ticks_diff(time.ticks_us(), start_time) # 경과 시간 업데이트

print(f"1second data: {sample_count}")

