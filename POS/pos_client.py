import functools
from lib import GUI_STDERR, GUI_STDOUT, output_message
from lib import APPDATA
from lib import TicketType
from lib import address, device_ip, router_ip
from lib import POSInterface
from lib import TICKET_QUEUED, TICKET_COMPLETE, TICKET_WORKING
from lib import OrderInterface
from POS import Order, NewOrder
import collections
import lib
import decimal
from operator import itemgetter
from time import localtime, strftime
from Printer import Printer
import contextvars
import websockets
import asyncio
import json
import logging
import functools
import subprocess
import os



# not yet implemented
def print_receipt(line, **kwargs):
    print(line, kwargs)

class POSProtocol(POSInterface):

    
    def __init__(self):
        super().__init__()
        self.network = False
        self.connected = False
        self.test_network_connection()
        self.connect_task = self.connect()
        self.receipt_printer = Printer("/dev/null")
        self.stdout = logging.getLogger(f"main.{self.client_id}.gui.stdout")
        self.stderr = logging.getLogger(f"main.{self.client_id}.gui.stderr")

    def get_ticket_no(self, result):
        if self.ticket_no is not None:
            ticket_no = "{:03d}".format(self.ticket_no)
            result.set(ticket_no)

    def new_order(self, payment_type, cash_given, change_due):
        order_dct = {"items":[ticket for ticket in Order()]}
        order_dct["total"] = Order().total
        order_dct["subtotal"] = Order().subtotal
        order_dct["tax"] = Order().tax
        order_dct["payment_type"] = payment_type
        order_dct["cash_given"] = cash_given
        order_dct["change_due"] = change_due
        
        task = self.loop.create_task(self.server_message("new_order", order_dct))
        def callback(task):
            ticket_no = task.result()
            ticket_no = "{:03d}".format(ticket_no)
            self.stdout.info(f"Received ticket no. {ticket_no}")

            
            lines_conf = [(ticket_no, Order().printer_style["ticket_no"])]

            for order in Order():
                lines_conf.extend(order.receipt())

            lines_conf.append(("Total: " + "$ {:.2f}".format(Order().total / 100), 
                    Order().printer_style["total"]))
            
            for line in lines_conf:
                self.receipt_printer.writeline(line[0], **line[1]) 
            NewOrder()
        task.add_done_callback(callback)
          
            
    def cancel_order(self, ticket_no):
        task = self.loop.create_task(self.server_message("cancel_order", ticket_no))
        def callback(task):
            _ticket_no = "{:03d}".format(ticket_no)
            result = task.result()
            message = "Cancelled ticket no. {ticket_no}, Change Due: {change_due}"
            if result:
                if result["payment_type"] == "Cash":
                    message = message.format(ticket_no=_ticket_no, change_due="-" + "{:.2f}".format(result["total"] / 100))
                else:
                    message = message.format(ticket_no=_ticket_no, change_due="-0.00")
                
                self.stdout.info(message)
        task.add_done_callback(callback)
    
    def modify_order(self, ticket_no, modified):
        original_dct = self.order_queue[str(ticket_no)]
        total = 0
        for i, ticket in enumerate(modified):
            total += ticket.total \
                    + ticket[6].total\
                    + ticket[7].total
            modified[i] = list(ticket)
            modified[i][6] = list(ticket[6])
            modified[i][7] = list(ticket[7])
            
        
        modified_dct = self.create_order(modified, 
                total,
                original_dct["payment_type"])

        task = self.loop.create_task(self.server_message("modify_order", (ticket_no, modified_dct)))
        def callback(task):
            _ticket_no = "{:03d}".format(ticket_no)
            result, reason = task.result()

            if result:
                message = "Modified ticket no. {} - Price difference: {}"
                difference = "{:.2f}".format((total - original_dct["total"]) / 100)
                # TODO log to sales.csv
                self.stdout.info(message.format(_ticket_no, difference))         
            else:
                self.stdout.critical(f"Failed to modify ticket no. {'{:03d}'.format(int(ticket_no))}. - {reason}")

        task.add_done_callback(callback)
        
    def get_order_info(self, ticket_no, *args):
        if args:
            return (self.order_queue[str(ticket_no)].get(arg) for arg in args)
        return ()
    
    def remove_completed(self):
        self.loop.create_task(
                self.server_message("remove_completed", None))

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
            ticket.parameters["status"] = TICKET_WORKING
        else:
            ticket.parameters["status"] = TICKET_QUEUED
    
    @staticmethod
    def create_order(ordered_items, total, payment_type):
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
    
    