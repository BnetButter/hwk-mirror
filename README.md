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

Patch Notes 3.02.003:
    Bug Fix:
        - Fixed a bug where changing item options without changing an item resulted in a no changes warning and preventing modify_order call to server.
        - Fixed a bug involving LCD Price Screen

Patch Notes 3.02.002
    General:
        - update readme patchnotes

Patch Notes 3.0.2.001
    Features:
        - Added price screen which shows total, cash, change, ticket number to customer.
        
Patch Notes 3.01.004
    Bug Fix:
        - Fixed bug where Toplevel widgets did not appear at the center of the screen as intended.
    General:
        - Removed 'ToplevelType' metaclass from lib.metaclass. 
        - Previously, ToplevelWidget subclassed MenuWidget and ToplevelType. ToplevelWidget now only subclasses only lib.MenuWidget.

Patch Notes 3.01.003
    General
        - updated readme patch notes.

Patch Notes 3.01.002
    Features
        - Added payment type editor. Accessible by cycling through "Menu Modes" on control panel. Note that unlike the Menu Editor which can be reinstanced to original state, the Reset button has no effect on payment type editor frame. Save and Apply still works as usual.
        - "Menu Mode" button is now much more versatile. It will lift any SingletonType class objects passed into its constructor. Or any class with a "instance" class attribute.

    General
        - ReinstanceType __call__ method has been changed. Previously it destroyed the instance. Now it only destroys the instance's children     before calling instance.__init__
        - Buttons on the Checkout tab for selecting a payment type has been extracted to its own class. Since payment types can now be edited, a new class (instance of ReinstanceType) was needed to reflect the changes in payment type.

Patch Notes 3.01.001
    Features
        - added a button to "Control Panel" console tab that opens the cash drawer
        - POS receipt printer will print without a server connection.
        - Client devices can now freely connect/disconnect from the server.
        
    Bug Fixes
        - Fixed an issue where cancelling an order on the POS resulted in failure to log all subsequent orders.
        - Fixed an issue where 'reinstancing' menu selection widget broke the OrderNavigator
        - Fixed an issue where not all menu items were displayed on menu selection widget.