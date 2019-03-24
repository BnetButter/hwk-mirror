# HWK-System

Copyright (C) 2018-2019 Heifers with a kick LLC

Author: Ziyu (Kevin) Lai


Hardware Devices:

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

High level policies and Device purposes

The server host may run several WebSocketServer objects. The primary server delegates one-off requests
to subroutines. These requests include placing an order, editing an order, completing an order, etc.
Any additional server objects are instantiated to issue continuous updates to connected clients.

1. The POS device runs two independent processes. 
    - websockets server host
    - POS GUI client.
    
    Server host
    
    - creates a shared global state between POS device and Display device

    - provides an interface for clients to modify global state such as

        - adding an order from the POS
        - marking an order as complete from Display
        - editing the menu from the POS
        - editing queued orders from POS
        - Time
    - Record keeper. Writes order information to file with info including

        - time of sale
        - payment type
        - items ordered
        - total, subtotal, tax
        - Transferring saved data

        Due to lack of internet access, the server host provides an interface for
        transferring sales data over LAN to an external device
    
    - Determines system time

        Since Raspberry Pi's do not have an onboard battery, cutting power to RPI
        for extended periods of will change system time. A GUI interface is provided for the user
        to change system time if necessary.

2. POS
    - The GUI provides an interface to 
        - create orders
        - cancel orders
        - edit orders

        - edit menu
        - global system shutdown

    - GUI widgets do not communicate with the server directly. Requests are forwarded to
      a client delegate object which exposes an interface to communicate with the server.

3. Display

    - The Display GUI exposes relevant information to the cook line,
      as well as an interface to mark an order as complete and
      advancing the queue. 
    
    - As with the POS, it does not interact with the server directly.
      all requests are forwarded to its own client delegate.