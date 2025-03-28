import serial
from datetime import datetime
import time
import tkinter as tk
import threading

ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
count = 0
start_period = time.time()  # 0.1초 단위의 시작 시간
data_log = []  # 0.1초당 샘플 개수를 기록할 리스트

class ADCGraph:
    """ADC 그래프"""
    def __init__(self, canvas, label):
        self.volt_values = []
        self.canvas = canvas
        self.label=label

    def update_adc_value(self, voltage):
        """시리얼 데이터를 받아서 그래프 업데이트"""
        self.volt_values.append(voltage)

        if len(self.volt_values) > 50:
            self.volt_values.pop(0)

        self.label.config(text=f"ADC Value: {voltage:.2f}", font=("Arial", 12))

        self.update_graph()         # 그래프 업데이트

    def update_graph(self):
        self.canvas.delete("adc_volt_graph")
        try:
            for i in range(len(self.volt_values) - 1):
                x1 = i * 10
                y1 = 175 - self.volt_values[i] * 10     # *10 = 전압 값을 10배 확대하여 변화를 강조
                x2 = (i + 1) * 10
                y2 = 175 - self.volt_values[i + 1] * 10
                self.canvas.create_line(x1, y1, x2, y2, fill="blue", width=2, tags="adc_volt_graph")
        except ValueError:
            pass

def serial_read_loop():
    """시리얼 데이터를 읽고 메인 스레드에서 업데이트 요청"""
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

                # 다음 0.1초 구간으로 넘어가면 이전 구간에 대한 데이터를 기록
                if current_period != int(start_period * 10) / 10.0:
                    period_start_time = datetime.fromtimestamp(start_period).strftime('%H:%M:%S.%f')[:-3]
                    period_end_time = datetime.fromtimestamp(start_period + 0.1).strftime('%H:%M:%S.%f')[:-3]

                    data_log.append(f"{period_start_time}~{period_end_time} 동안 받은 샘플 개수: {count}")

                    start_period = current_period  # 다음 0.1초 구간
                    count = 0  # 샘플 개수 초기화

                count += 1  # ADC 값 수신 시 카운트 증가
                timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S.%f]")      # 마이크로 초 까지 출력

                root.after(0, adc_graph.update_adc_value, voltage)  # 메인 스레드에서 그래프 업데이트
                root.after(0, update_labels, timestamp)  # 메인 스레드에서 라벨 업데이트

        except serial.SerialException as e:
            print(f"Failed to read from Pico: {e}")
            break

def update_labels(timestamp):
    """타임스탬프 및 송수신 시간 라벨 업데이트"""
    timestamp_label.config(text=f"Timestamp: {timestamp}")

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

adc_label = tk.Label(root, text="-", font=("Arial", 12))
adc_label.place(x=50, y=400)

timestamp_label = tk.Label(root, text="-", font=("Arial", 12))
timestamp_label.place(x=50, y=450)

adc_graph = ADCGraph(canvas_ADC_rect, adc_label)
serial_thread = threading.Thread(target=serial_read_loop, daemon=True)
serial_thread.start()

root.mainloop()
ser.close()
