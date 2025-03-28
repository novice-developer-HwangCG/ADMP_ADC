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

class ADCGraph:
    """ADC 그래프"""
    def __init__(self, canvas):
        self.volt_values = []
        self.canvas = canvas

    def update_adc_value(self, voltage):
        """시리얼 데이터를 받아서 그래프 업데이트"""
        self.volt_values.append(voltage)

        if len(self.volt_values) > 50:
            self.volt_values.pop(0)

        self.update_graph()         # 그래프 업데이트

    def update_graph(self):
        self.canvas.delete("adc_volt_graph")
        try:
            for i in range(len(self.volt_values) - 1):
                x1 = i * 10
                y1 = 175 - self.volt_values[i] * 10     # *10 = 전압 값을 그래프 캔버스의 픽셀 단위로 확대하여 시각적으로 더 잘 보이게 하기 위함
                x2 = (i + 1) * 10
                y2 = 175 - self.volt_values[i + 1] * 10
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="adc_volt_graph")
        except ValueError:
            pass

def serial_read_loop():
    """시리얼 데이터를 읽고 메인 스레드에서 업데이트 요청"""
    global count, start_period
    while True:
        try:
            if ser.in_waiting > 0:
                current_time = time.time()
                start_time = time.time()  # 송수신 시작 시간 기록

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

                timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S.%f]")  # 마이크로초까지 출력
                # elapsed_time = (time.time() - start_time) * 1000  # 밀리초(ms) 단위 변환

                root.after(0, adc_graph.update_adc_value, voltage)  # 메인 스레드에서 그래프 업데이트
                # root.after(0, update_labels, timestamp, elapsed_time)  # 메인 스레드에서 라벨 업데이트

        except serial.SerialException as e:
            print(f"Failed to read from Pico: {e}")
            break

#def update_labels(timestamp, elapsed_time):
def update_labels(timestamp):
    """타임스탬프 및 송수신 시간 라벨 업데이트"""
    timestamp_label.config(text=f"Timestamp: {timestamp}")
    # elapsed_time_label.config(text=f"Trans time: {elapsed_time:.2f} ms")

def save_data():
    """파일 저장 경로 및 파일명 형식 지정하여 저장"""
    save_dir = "/home/jetpack/Desktop/admp_adc/save_log"
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    
    file_name = datetime.now().strftime("%Y-%m-%d-%H-%M-%S") + "-admp-log.txt"
    file_path = os.path.join(save_dir, file_name)

    with open(file_path, 'w') as file:
        for log_entry in data_log:
            file.write(f"{log_entry}\n")
    
    print(f"Data saved to {file_path}")

root = tk.Tk()
root.title("ADMP ADC")
root.geometry("550x500")

ADC_rect = tk.Frame(width=450, height=350, bg="white", relief="solid", bd=1)
ADC_rect.place(x=50, y=20)

canvas_ADC_rect = tk.Canvas(ADC_rect, width=450, height=350, bg="white")
canvas_ADC_rect.pack()

Vol_val = ["+5V", "+4V", "+3V", "+2V", "+1V", "  0V"]
Vol_y_pos = [17, 84, 151, 218, 285, 352]
for name, y in zip(Vol_val, Vol_y_pos):
    Vol_label = tk.Label(root, text=name, font=("Helvetica", 10))
    Vol_label.place(x=10, y=y)

timestamp_label = tk.Label(root, text="-", font=("Arial", 12))
timestamp_label.place(x=50, y=400)

# elapsed_time_label = tk.Label(root, text="-", font=("Arial", 12))
# elapsed_time_label.place(x=350, y=400)

save_button = tk.Button(root, text="Save Data", command=save_data)
save_button.place(x=50, y=450)

adc_graph = ADCGraph(canvas_ADC_rect)
serial_thread = threading.Thread(target=serial_read_loop, daemon=True)
serial_thread.start()

root.mainloop()
ser.close()
