## IDW01M1 filesystem updater

This repository contains python script and serial passthrough program for STM32
Nucleo. Python script uploads HTML/CSS/JS files to the external Flash memory of
the Wi-Fi expansion board.

Wi-Fi expansion board is connected to the Nucleo board which is connected to a
PC. I should mention that can be used without Necleo board. What is needed is
just serial interface to the Wi-Fi board, therefore, you can
connect IDW01M1 directly to a serial <-> USB adapter.

## Instruction

1. Connect Wi-Fi expansion board to the Nucleo and connect it to the PC
2. Compile and upload `src/main.cpp` program (I used platformio to manage my
   project)
3. Open serial monitor on your PC (for example: GtkTerm (Linux), Arduino IDE
   (windows))
4. Press reset button on your board. After that you should see some initial 
   messages of the Nucleo application.

```
==========================================================
Communication with the Wi-Fi board
==========================================================
Enter passthrogh mode:
```

5. Now we should test that communication is working correctly. If you type `AT`
   command you should get `OK` response.

```
==========================================================
Communication with the Wi-Fi board
==========================================================
Enter passthrogh mode:
AT

OK
```

   This command do nothing but let us know that communication is working. Now
   you can close the serial monitor.
6. Next, we need to configure Python script.
   


### Links

* [IDW01M1 Wi-Fi expansion board](http://www.st.com/content/st_com/en/products/ecosystems/stm32-open-development-environment/stm32-nucleo-expansion-boards/stm32-ode-connect-hw/x-nucleo-idw01m1.html)
* [STM32 Nucleo L476RG](http://www.st.com/en/evaluation-tools/nucleo-l476rg.html)
* [PlatformIO](http://platformio.org/)
