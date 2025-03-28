import serial
from datetime import datetime
import time
import os

# rtscts=False 하드웨어 플로우 제어 비활성화
ser = serial.Serial('/dev/ttyTHS1', 1000000, timeout=0.001, rtscts=False, dsrdtr=False)
count = 0
start_period = time.time()  # 0.1초 단위의 시작 시간
data_log = []  # 0.1초당 샘플 개수를 기록할 리스트
buffer_size = 1024  # 적당한 크기의 버퍼 설정

try:
    while True:
        # 데이터를 빠르게 읽기 위해 버퍼에 있는 데이터를 모두 읽음
        # line = ser.read_until(b'\n').decode('utf-8').strip()
        # 디코딩 제거
        # line = ser.readline().strip()
        # line = ser.readline().decode('utf-8').strip()
        if ser.in_waiting > 0:
            # line = ser.read(ser.in_waiting).decode('utf-8').strip()
            data = ser.read(min(ser.in_waiting, buffer_size)).strip()
        if not data:
            continue
        try:
            voltage = float(data)  # 수신된 ADC 값
        except ValueError:
            print(f"Invalid ADC value received: {data}")
            continue  # 잘못된 값은 무시하고 다음 루프로

        # 현재 0.1초 구간을 계산
        current_time = time.time()
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
        print(f"{timestamp} ADC: {voltage:.2f}")

except KeyboardInterrupt:       # ctrl+c 키 입력시 자동 저장 
    print("exit.")
finally:
    ser.close()
    save_dir = "/home/jetpack/Desktop/admp_adc/save_log"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    file_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-admp-log.txt"
    file_path = os.path.join(save_dir, file_name)

    with open(file_path, 'w') as file:
        for log_entry in data_log:
            file.write(f"{log_entry}\n")
    
    print(f"Data saved to {file_path}")
