import serial
from datetime import datetime
import time
import os

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
count = 0
start_period = time.time()  # 0.1초 단위의 시작 시간
data_log = []  # 0.1초당 샘플 개수를 기록할 리스트

try:
    while True:
        if ser.in_waiting > 0:
            current_time = time.time()
            start_time = time.time()
            line = ser.readline().decode('utf-8').strip()

            try:
                voltage = float(line)  # 수신된 ADC 값
            except ValueError:
                print(f"Invalid ADC value received: {line}")
                continue  # 잘못된 값은 무시하고 다음 루프로

            # 현재 0.1초 구간을 계산
            current_period = int(current_time * 10) / 10.0

            # 다음 0.1초 구간으로 넘어가면 이전 구간에 대한 데이터를 기록
            if current_period != int(start_period * 10) / 10.0:
                period_start_time = datetime.fromtimestamp(start_period).strftime('%H:%M:%S.%f')[:-3]
                period_end_time = datetime.fromtimestamp(start_period + 0.1).strftime('%H:%M:%S.%f')[:-3]

                data_log.append(f"{period_start_time}~{period_end_time} 동안 받은 샘플 개수: {count}")

                start_period = current_period  # 다음 0.1초 구간
                count = 0  # 샘플 개수 초기화

            count += 1  # ADC 값 수신 시 카운트 증가

            timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S.%f]")  # 수신 타임스탬프 기록
            # elapsed_time = (time.time() - start_time) * 1000  # 송수신에 걸린 시간 계산 ms 단위 변환
            # | Trans time: {elapsed_time:.2f} ms
            print(f"{timestamp} ADC: {voltage:.2f}")

except KeyboardInterrupt:       # ctrl+c 키 입력시 자동 저장 
    print("exit.")
finally:
    ser.close()
    with open("sample_count_log.txt", "w") as f:
        for log_entry in data_log:
            f.write(log_entry + "\n")
