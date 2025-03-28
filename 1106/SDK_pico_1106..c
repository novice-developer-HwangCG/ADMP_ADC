#include "pico/stdlib.h"
#include "hardware/uart.h"
#include "hardware/gpio.h"
#include "hardware/adc.h"
#include <stdio.h>

#define UART_ID uart0
#define BAUD_RATE 1000000
#define UART_TX_PIN 0
#define UART_RX_PIN 1
#define ADC_PIN 26

void configure_uart() {
    uart_init(UART_ID, BAUD_RATE);
    gpio_set_function(UART_TX_PIN, GPIO_FUNC_UART);
    gpio_set_function(UART_RX_PIN, GPIO_FUNC_UART);
    uart_set_hw_flow(UART_ID, false, false);
    uart_set_format(UART_ID, 8, 1, UART_PARITY_NONE);
    uart_set_fifo_enabled(UART_ID, true);       // FIFO를 활성화하여 버퍼 크기를 최대화
}

void configure_adc() {
    adc_init();
    adc_gpio_init(ADC_PIN);
    adc_select_input(0); 
}

uint16_t read_adc_value() {
    return adc_read();
}

int main() {
    stdio_init_all();
    configure_uart();
    configure_adc();

    char output[20];
    while (true) {
        const float conversion_factor = 3.3f / (1 << 12);
        uint16_t mic_value = read_adc_value();
        sprintf(output, "%.2f\n", mic_value * conversion_factor);
        uart_puts(UART_ID, output);
        sleep_us(10);               // 지연 10마이크로초 => 0.00001초
    }
}
