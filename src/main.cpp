#include "mbed.h"

#include "config.h"

// Init serial with PC
Serial pc(USBTX, USBRX);
// Init serial with Wi-Fi board
Serial wifi(D8, D2);

void passthrogh_mode(Serial * wifi, Serial * pc){
    int8_t buffer = 0;
    while(1){
        if(pc -> readable()){
            buffer = pc -> getc();
            wifi -> putc(buffer);
        }

        if(wifi -> readable()){
            buffer = wifi -> getc();
            pc -> putc(buffer);
        }
    }
}

int main()
{
    int err = 0;
    /* Set up Serial link with PC and Wi-Fi module */
    pc.baud(115200);
    wifi.baud(115200);

    DEBUGP(("==========================================================\r\n"));
    DEBUGP(("Communication with the Wi-Fi board\r\n"));
    DEBUGP(("==========================================================\r\n"));

    /* Go into passthrough mode */
    printf("Enter passthrogh mode:\r\n");
    passthrogh_mode(&wifi, &pc);
}

