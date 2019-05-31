# HWK-System

Copyright (C) 2018-2019 Heifers with a kick LLC
Author: Ziyu (Kevin) Lai

Devices:

1. POS
    - Raspberry Pi 3 B+
    - Toguard 1280x800 10.1" Touch Screen
    - Numpad Keyboard

2. Display
    - Raspberry Pi 3 B+
    - Acer 1920x1080 22" Monitor
    - Numpad Keyboard

3. Linksys WRT54G2 Router

4. External data transfer device*

5. 2x Adafruit Thermal Printers

6. Cash drawer (modified Epson RJ11 interface)

Patch Notes 3.01.001
Features
    - added a button to "Control Panel" console tab that opens the cash drawer
    - POS receipt printer will print without a server connection.
    - Client devices can now freely connect/disconnect from the server.
        

Bug Fixes
    - Fixed an issue where cancelling an order on the POS resulted in failure to log all subsequent orders.
    - Fixed an issue where 'reinstancing' menu selection widget broke the OrderNavigator
    - Fixed an issue where not all menu items were displayed on menu selection widget.