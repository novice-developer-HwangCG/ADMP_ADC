import serial
from datetime import datetime
import time
import tkinter as tk
import threading
import os

ser = serial.Serial('/dev/ttyTHS1', 912600, timeout=0.01)
count = 0
start_period = time.time()  # 0.1초 단위의 시작 시간
data_log = []  # 0.1초당 샘플 개수를 기록할 리스트

def serial_read_loop():
    """시리얼 데이터를 읽고 메인 스레드에서 업데이트 요청"""
    global count, start_period
    while True:
        try:
            if ser.in_waiting > 0:
                current_time = time.time()
                adc_value = ser.readline().decode('utf-8').strip()
                
                try:
                    voltage = float(adc_value)  # 수신된 ADC 값
                except ValueError:
                    print(f"Invalid ADC value received: {adc_value}")
                    continue  # 잘못된 값은 무시하고 다음 루프로

                current_period = int(current_time * 10) / 10.0

                # 새로운 0.1초 구간이면 이전 구간 로그 기록
                if current_period != int(start_period * 10) / 10.0:
                    period_start_time = datetime.fromtimestamp(start_period).strftime('%H:%M:%S.%f')[:-3]
                    period_end_time = datetime.fromtimestamp(start_period + 0.1).strftime('%H:%M:%S.%f')[:-3]
                    data_log.append(f"{period_start_time}~{period_end_time}, 샘플 개수: {count}")

                    start_period = current_period  # 새로운 0.1초 구간 시작
                    count = 0  # 샘플 개수 초기화

                count += 1  # ADC 값 수신 시 카운트 증가
                timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S.%f]")[:-3]  # 마이크로초까지 출력

                root.after(0, lambda: update_labels(timestamp, voltage))

        except serial.SerialException as e:
            print(f"Failed to read from Pico: {e}")
            break

def update_labels(timestamp, voltage):
    """타임스탬프 및 ADC값 라벨 업데이트"""
    timestamp_label.config(text=f"Timestamp: {timestamp}")
    adc_label.config(text=f"ADC_Value: {voltage}")

def save_data():
    """파일 저장 경로 및 파일명 형식 지정하여 저장"""
    save_dir = "/home/jetpack/Desktop/admp_adc/save_log"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    # 현재 시간을 기준으로 파일명 생성 (YY-MM-DD-HH-MM-SS 형식)
    file_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-admp-log.txt"
    file_path = os.path.join(save_dir, file_name)

    with open(file_path, 'w') as file:
        for log_entry in data_log:
            file.write(f"{log_entry}\n")
    
    print(f"Data saved to {file_path}")

root = tk.Tk()
root.title("ADMP ADC")
root.geometry("300x200")

adc_label = tk.Label(root, text="-", font=("Arial", 12))
adc_label.place(x=50, y=50)

timestamp_label = tk.Label(root, text="-", font=("Arial", 12))
timestamp_label.place(x=50, y=100)

save_button = tk.Button(root, text="Save Data", command=save_data)
save_button.place(x=100, y=150)

serial_thread = threading.Thread(target=serial_read_loop, daemon=True)
serial_thread.start()

def on_closing():
    print("Exit")
    ser.close()
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()
