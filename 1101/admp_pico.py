from machine import ADC, Pin
import utime
import sys

# ADMP401의 아날로그 신호를 읽기 위한 ADC 설정 (GPIO26 사용)
mic = ADC(Pin(26))  # A0 핀에 연결 (GP26)

uart = sys.stdout

while True:
    mic_value = mic.read_u16()  # 16비트 해상도로 아날로그 값 읽기
    voltage = mic_value * 3.3 / 65535
    
    # timestamp = utime.localtime()
    
    #timestamp_str = f"[{timestamp[0]:04d}-{timestamp[1]:02d}-{timestamp[2]:02d} {timestamp[3]:02d}:{timestamp[4]:02d}:{timestamp[5]:02d}]"
    # {timestamp_str}
    uart.write(f"{voltage}\n")

    utime.sleep(0.001)  #0.1