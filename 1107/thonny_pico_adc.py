import machine
import time

adc = machine.ADC(26)   # ADC 핀 (GP26: ADC0)

# 샘플링 주파수 설정
sampling_rate = 128000  # 128kHz
sampling_interval = 1 / sampling_rate  # 샘플링 간격
sample_count = 0  # 1초 동안 샘플링한 데이터 개수

# 1초 동안 샘플링을 시작
start_time = time.ticks_us()  # 시작 시간 (마이크로초)
elapsed_time = 0

while elapsed_time < 1000000:  # 1초 동안 실행 (1000000 마이크로초 = 1초)
    adc_value = adc.read_u16()  # ADC 16bit 65535
    sample_count += 1  # 샘플 카운트 증가
    
    time.sleep_us(int(sampling_interval * 1e6))  # 샘플링 주기 동안 마이크로초 단위로 대기

    elapsed_time = time.ticks_diff(time.ticks_us(), start_time) # 경과 시간 업데이트
    # print(f"ADC : {adc_value}")

# 결과 출력
print(f"1 second data: {sample_count}")

