from machine import ADC, Pin, UART
import utime
import sys

# ADMP401의 아날로그 신호를 읽기 위한 ADC 설정 (GPIO26 사용)
mic = ADC(Pin(26))  # A0 핀에 연결 (GP26)

#uart = UART(0, baudrate=115200, tx=Pin(0), rx=Pin(1))  # UART0, 보드레이트 1 Mbps
uart = sys.stdout

while True:
    mic_value = mic.read_u16()  # 16비트 해상도로 아날로그 값 읽기
    voltage = mic_value * 3.3 / 65535
    
    uart.write(f"{voltage:.2f}\n")

    # 지연 최소화 필요 시 주석 해제 사용가능
    utime.sleep(0.001)  #0.001 -> 1000 마이크로

