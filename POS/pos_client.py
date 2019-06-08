from operator import itemgetter
from time import localtime, strftime
from Printer import Printer
from CashDrawer import Drawer
from lib import GUI_STDERR, GUI_STDOUT, output_message
from lib import APPDATA
from lib import TicketType
from lib import address, device_ip, router_ip
from lib import POSInterface
from lib import TICKET_QUEUED, TICKET_COMPLETE, TICKET_WORKING
from lib import OrderInterface
from POS import Order, NewOrder
from POS.lcd_display import LCDScreen
import POS
import collections
import lib
import decimal
import functools
import websockets
import asyncio
import json
import logging
import functools
import subprocess
import os
import time


class POSProtocol(POSInterface):

    def __init__(self):
        super().__init__()
        self.network = False
        self.connected = False
        self.test_network_connection()
        self.connect_task = self.connect()
        self.receipt_printer = Printer()
        self.cash_drawer = Drawer()
        self.screen = LCDScreen()
        self.stdout = logging.getLogger(f"main.{self.client_id}.gui.stdout")
        self.stderr = logging.getLogger(f"main.{self.client_id}.gui.stderr")
        self.last_total = 0
        self.last_no = 0
        self.last_tab = ""
        self.pause_screen_update = False
    

    def get_ticket_no(self, result):
        if self.ticket_no is not None:
            ticket_no = "{:03d}".format(self.ticket_no)
            result.set(ticket_no)
    
    @staticmethod
    def _new_order(payment_type, cash_given, change_due):
        order_dct = {"items":list(ticket for ticket in Order())}
        order_dct["total"] = Order().total 
        order_dct["subtotal"] = Order().subtotal
        order_dct["tax"] = Order().tax
        order_dct["payment_type"] = payment_type
        order_dct["cash_given"] = cash_given
        order_dct["change_due"] = change_due
        
        # set print flag

        cnt_all = 0 # number of non-NULL items
        cnt_reg = 0 # number of items with register flag
        for ticket in Order():
            items = filter(lambda item: item.name,(ticket, ticket[6], ticket[7]))
            for item in items:
                cnt_all += 1
                if item.parameters.get("register", False):
                    cnt_reg += 1
                    item.parameters["status"] = lib.TICKET_COMPLETE
        
        if cnt_all == cnt_reg:
            order_dct["print"] = False
        else:
            order_dct["print"] = lib.PRINT_NEW
        return order_dct

    def _new_receipt_content(self, payment_type, cash_given, change_due):
        if self.ticket_no is None:
            self.ticket_no = 1
        lines_conf = [
                ("{:03d}".format(self.ticket_no), Order().printer_style["ticket_no"]),
                (time.strftime("%D %I:%M:%S %p", time.localtime()),
                        {"justify":bytes('C', "utf-8")})]
        
        for order in Order():
            lines_conf.extend(order.receipt())

        fmter = "$ {:.2f}".format
        print_strs = [
            "Subtotal: "     + fmter(Order().subtotal / 100),
            "     Tax: "     + fmter(Order().tax / 100),
            "   Total: "     + fmter(Order().total / 100),
            " ",
            "Payment Type: "  + payment_type,
            "  Cash Given: " + fmter(cash_given / 100),
            "  Change Due: " + fmter(change_due / 100)
        ]
        
        price_style = Order().printer_style["total"]
        if payment_type == "Cash":
            lines_conf.extend((line, price_style) for line in print_strs)
        else:
            lines_conf.extend((line, price_style) for line in print_strs[:5])
        return lines_conf

    def _cancel_receipt_content(self, order, ticket_no):
        lines_conf = [
                ("CANCEL " + "{:03d}".format(int(ticket_no)), Order().printer_style["ticket_no"]),
                (time.strftime("%D %I:%M:%S %p", time.localtime()),
                        {"justify":bytes('C', "utf-8"), "size":bytes('S', "utf-8")})]
        
        price_style = Order().printer_style["total"]
        lines_conf.append(("Payment Type: "  + order["payment_type"], price_style))
        lines_conf.append(("  Change Due: " + "{:.2f}".format(order["total"] / 100), price_style))
        return lines_conf

    def _modify_receipt_content(self, original_order,
            new_order, cash_given, change_due, difference) -> (list, int):
        
        lines_conf = [
                ("MODIFY " + "{:03d}".format(self.ticket_no), Order().printer_style["ticket_no"]),
                (time.strftime("%D %I:%M:%S %p", time.localtime()),
                        {"justify":bytes('C', "utf-8"), "size":bytes('S', "utf-8")},
                ("[original]", {})),
        ]

        item_difference_count = 0
        for original, new in zip(original_order["items"], new_order):
            original = Order().convert_to(*original)
            line, diff = Order().compare(original, new)
            item_difference_count += diff
            lines_conf.extend((l, Order().printer_style["item"]) for l in line)
    
        price_style = Order().printer_style["total"]
        payment_type = original_order["payment_type"]
        lines_conf.append(("Difference  : " + "{:.2f}".format(difference / 100), price_style))
        lines_conf.append(("Payment Type: "  + payment_type, price_style))
        if payment_type == "Cash":
            lines_conf.append(("  Cash Given: " + "{:.2f}".format(cash_given / 100), price_style))
            lines_conf.append(("  Change Due: " + "{:.2f}".format(difference / 100), price_style))
        
        return lines_conf, item_difference_count
    

    async def print_receipt(self, receipt, *args):
        if lib.DEBUG:
            print("\n".join(line[0] for line in receipt))
        
        for line in receipt:
            self.receipt_printer.writeline(line[0], **line[1])
            await asyncio.sleep(1/60)
        self.receipt_printer.writeline("\n\n\n")
        await asyncio.sleep(1/60)

    async def update_screen(self, cash, change, pause=False, ticket_no=None, postfix=""):
        await self.screen.set_cash(cash)
        await self.screen.set_change(change)
        if ticket_no is not None:
            await self.screen.set_ticket_no(ticket_no, postfix)


    def new_order(self, payment_type, cash_given, change_due):
        order_dct = self._new_order(
                payment_type, cash_given, change_due)

        if payment_type == "Cash":
            self.stdout.info("({})  Change Due: {:.2f}".format(self.ticket_no, change_due / 100))
            self.cash_drawer.open()
            self.loop.create_task(self.update_screen(cash_given, change_due))
        else:
            self.loop.create_task(self.update_screen(None, None))

        receipt = self._new_receipt_content(payment_type, cash_given, change_due)
        # unblocks printer.writeline
        self.loop.create_task(self.print_receipt(receipt))
        task = self.loop.create_task(self.server_message("new_order", order_dct))
        NewOrder()
        self.ticket_no += 1
        
        def callback(task):
            ticket_no = task.result()
            ticket_no = "{:03d}".format(ticket_no)
            self.stdout.info(f"Received ticket no. {ticket_no}")

        task.add_done_callback(callback)

    def cancel_order(self, ticket_no):
        # check if order still exists serverside
        order = self.order_queue.get(str(ticket_no))
        if order is None:
            return self.stdout.warning("Cannot find ticket no. {:03d}".format(ticket_no))
        
        assert isinstance(order, dict)
        message = "Cancelled ticket no. {:03d}, Change Due: {}"
        
        if order["payment_type"] == "Cash":
            self.cash_drawer.open()
            message = message.format(ticket_no, -1 * order["total"] / 100)
       
            self.loop.create_task(self.update_screen(None, -1 * int(order["total"]),
                pause=True, ticket_no=ticket_no, postfix="(Cancel)"))
            if lib.DEBUG:
                print("drawer open... ")
        else:
            message = message.format(ticket_no, order["payment_type"])
        self.stdout.info(message)
        
        # print receipt
        cancel_receipt = self._cancel_receipt_content(order, ticket_no)
        self.loop.create_task(self.print_receipt(cancel_receipt))
        task = self.loop.create_task(self.server_message("cancel_order", ticket_no))

        def callback(task):
            if task.result():
                self.stdout.info("Cancel success")
            else:
                self.stdout.info("Cancel failure")
        task.add_done_callback(callback)

    def modify_order(self, ticket_no, modified, cash_given, change, difference):
        original_dct = self.order_queue[str(ticket_no)]
        # check cash given is greater than difference only 
        # if original payment type is cash.
        if change == "- - -" \
                and difference \
                and original_dct["payment_type"] == "Cash":
            return self.stdout.info("Cash given is less than difference")

        cash_given = int(cash_given.replace(".", ""))
        try:
            change = int(change.replace(".", ""))
        except:
            change = 0

        # shows changes made to original order if changes were made
        # otherwise shows original order
        modify_receipt, changes_made_cnt = self._modify_receipt_content(
                    original_dct,
                    modified,
                    cash_given,
                    change,
                    difference)

        if not changes_made_cnt:            
            return self.stdout.info("No changes made to ticket no. {:03d}".format(int(ticket_no)))        
        
        total = 0
        for i, ticket in enumerate(modified):
            total += self.get_total(ticket, ticket[6], ticket[7])
            # MutableTicket object is not json serializable
            # and im too lazy to add decoder/encoder function
            modified[i] = list(ticket)
            modified[i][6] = list(ticket[6])
            modified[i][7] = list(ticket[7])

        modified_dct = self.create_order(modified,
                total,
                original_dct["payment_type"])
        
        modified_dct["print"] = lib.PRINT_MOD
        # print message to console
        message = "Modified ticket no. {} - Price difference: {}"
        difference = "{:.2f}".format((total - original_dct["total"]) / 100)
        self.stdout.info(message.format(ticket_no, difference))

        # open cash drawer if necessary
        if original_dct["payment_type"] == "Cash"\
                        and difference != "0.00" \
                        and change:
            self.stdout.info("  Change Due: {:.2f}".format(change / 100))
            self.loop.create_task(self.update_screen(cash_given, change))
            if lib.DEBUG:
                print("drawer open...")
        
    

        # create non-blocking print task
        self.loop.create_task(self.print_receipt(modify_receipt))

        # send server request
        task = self.loop.create_task(self.server_message("modify_order", (ticket_no, modified_dct)))
    
        def callback(task):
            _ticket_no = "{:03d}".format(ticket_no)
            result, reason = task.result()
            if result:
                self.stdout.info("Server received modify request")
            else:
                self.stdout.critical(f"Server failed to execute modify request - '{reason}'")
        task.add_done_callback(callback)

    def get_order_info(self, ticket_no, *args):
        if args:
            return (self.order_queue[str(ticket_no)].get(arg) for arg in args)
        return ()

    def edit_menu(self, new_menu):
        task = self.loop.create_task(
                self.server_message("edit_menu", new_menu))
        def done_callback(task):
            result, reason = task.result()
            if result:
                self.stdout.info("Menu saved")
            else:
                self.stdout.info("WARNING - Failed to save menu")
                self.stderr.warning("WARNING - Failed to save menu")
        task.add_done_callback(done_callback)
        
    def get_order_status(self, ticket_no, *args):
        tickets = self.order_queue.get(str(ticket_no))["items"]
        if tickets is None:
            return 100

        num_items = 0
        num_completed = 0
        for ticket in tickets:
            ticket = ticket[:6], ticket[6], ticket[7]
            for item in ticket:
                if item[1]:
                    num_items += 1
                if item[1] and item[5].get("status") == TICKET_COMPLETE:
                    num_completed += 1
        return int((num_completed/num_items) * 100)

    def get_time(self):
        raise NotImplementedError

    def global_shutdown(self, shutdown_in):
        self.loop.create_task(self.server_message("global_shutdown", shutdown_in))
    
    def edit_order(self):
        raise NotImplementedError
    
    @staticmethod
    def _item_total(item):
        if not item.name:
            return 0
        total = item.price
        for option in item.selected_options:
            total += item.options[option]
        return total

    def get_total(self, item, addon1, addon2):
        assert all(isinstance(type(_item), lib.TicketType) for _item in (item, addon1, addon2))
        total = self._item_total(item)
        if item.category in Order().two_sides \
                or item.category in Order().no_addons:
            return total
        
        if item.category not in Order().include_drinks:
            for addon in (addon1, addon2):
                if addon.category == "Drinks":
                    total += self._item_total(addon)

        if item.category not in Order().include_sides:
            for addon in (addon1, addon2):
                if addon.category == "Sides":
                    total += self._item_total(addon)
        return total

    @staticmethod
    def set_ticket_status(ticket):
        if ticket.parameters["register"]:
            ticket.parameters["status"] = TICKET_COMPLETE
        else:
            ticket.parameters["status"] = TICKET_QUEUED
    
    @staticmethod
    def create_order(ordered_items, total, payment_type):
        """create a modified order"""
        order_dct = {
            "items": ordered_items,
            "payment_type":payment_type,
            "total": total}
        
        tax_scale = int((Order().taxrate * 100) + 10000)
        subtotal = int(decimal.Decimal((total * 100) 
                / tax_scale).quantize(
                decimal.Decimal('0.01'),
                    rounding=decimal.ROUND_HALF_DOWN) * 100)

        tax = total - subtotal
        order_dct["subtotal"] = subtotal
        order_dct["tax"] = tax    
        return order_dct
    
    def print_invoice(self):
        month = 2592000
        current_time = int(time.time())
        start_time = current_time - month
        for payment_type in (p for p in Order().payment_types if p != "Cash" and p != "Check"):
            args = [
                    "awk "
                    f"-vstart={start_time}",
                    f"-vend={current_time}",
                    "-vpayment_type=" + payment_type,
                    "-f" + os.path.join(os.getcwd(), "hwk/POS/invoice.awk "),
                    lib.SALESLOG + " ",            
                ]
            
            if not lib.DEBUG:
                args.append("> /dev/serial0")

            subprocess.call(" ".join(args), shell=True)
    
    # should combine top and bottom function.
    # but no receipt printer at the moment for testing.
    # safer to just add another function and awk script.
    def print_daily_sales(self):
        day = 86400
        current_time = int(time.time())
        start_time = current_time - day
        args = [
            "awk ",
            f"-vstart={start_time}",
            f"-vend={current_time}",
            "-f" + os.path.join(os.getcwd(), "hwk/POS/sales.awk "),
            lib.SALESLOG + " ",
        ]
        
        if not lib.DEBUG:
            args.append("> /dev/serial0")
        return subprocess.call(" ".join(args), shell=True)
    
    def open_drawer(self):
        self.cash_drawer.open()
    
    def update_total(self, tabbed_frame, modify_tab_name, editor):
        async def update():
            while True:
                await asyncio.sleep(1/60)
                current_tab = tabbed_frame.current()
                if current_tab == self.last_tab:
                    if current_tab == "Orders" or current_tab == "Checkout":
                        await self.screen.set_ticket_no(self.last_no)
                        if not self.last_total:
                            self.last_total = Order().total
                            continue
                        await self.screen.set_total(self.last_total)
                     
                    elif current_tab == "Processing":
                        if editor.is_gridded:
                            await self.screen.set_ticket_no(editor.ticket_no, "(edit)")
                            await self.screen.set_total(editor.difference)
                        else:
                            await self.screen.set_total(None)
                            continue
                else:
                    self.last_tab = current_tab
                    self.last_no = self.ticket_no
                    self.last_total = None
                    await self.screen.set_ticket_no(None)
                    await self.screen.set_total(None)
                    await self.screen.set_change(None)
                    await self.screen.set_cash(None)
        self.create_task(update())