from operator import itemgetter
from .options import GroupEditOptions, EditOptions
import collections
import lib
import tkinter as tk


ORDER_SELECT = 0
ORDER_EDIT = 1

class ItemTicket(lib.Ticket, metaclass=lib.TicketType):

    def __new__(cls, menu_item, addon1, addon2, 
            selected_options=None, parameters=None,
            selected_options_addon1=None,selected_options_addon2=None,
            parameters_addon1=None,parameters_addon2=None):

        if selected_options is None:
            selected_options = list()
        if parameters is None:
            parameters = cls._param_init(menu_item)
        

        p0 = parameters
        p1 = (cls._param_init(menu_item)
                if parameters_addon1 is None
                else parameters_addon1)
        p2 = (cls._param_init(menu_item)
                if parameters_addon2 is None
                else parameters_addon2)

        # 'register' value doesn't carry over since item starts as NULL
        if addon1.category in Order.register:
            p1["register"] = True
        if addon2.category in Order.register:
            p2["register"] = True

        addon1, addon2 = lib.Ticket(addon1, parameters=p1), \
                lib.Ticket(addon2, parameters=p2)

        result = tuple.__new__(cls, (*menu_item, list(selected_options), p0, addon1, addon2))

        if selected_options_addon1 is not None:
            result.addon1.selected_options = selected_options_addon1
        if selected_options_addon2 is not None:
            result.addon2.selected_options = selected_options_addon2
        return result

    def get(self, i):
        if i == 0:
            return self
        elif i == 1:
            return self.addon1
        elif i == 2:
            return self.addon2
        else:
            raise IndexError

    def set(self, i, item):
        if i == 0:
            return ItemTicket(item, self.addon1.menu_base, self.addon2.menu_base,
                    selected_options=(opt for opt in self.selected_options if opt in item.options),
                    selected_options_addon1=self.addon1.selected_options,
                    selected_options_addon2=self.addon2.selected_options,
                    parameters=(self.parameters if self == item else None),
                    parameters_addon1=self.addon1.parameters,
                    parameters_addon2=self.addon2.parameters)
        elif i == 1:
            return ItemTicket(self.menu_base, item,
                    self.addon2.menu_base,
                    selected_options=self.selected_options,
                    selected_options_addon1=(opt for opt in self.addon1.selected_options if opt in item.options),
                    selected_options_addon2=self.addon2.selected_options,
                    parameters=self.parameters,
                    parameters_addon1=(self.addon1.parameters if self.addon1 == item else None),
                    parameters_addon2=self.addon2.parameters)
        elif i == 2:
            return ItemTicket(self.menu_base, self.addon1.menu_base, item,
                    selected_options=self.selected_options,
                    selected_options_addon1=self.addon1.selected_options,
                    selected_options_addon2=(opt for opt in self.addon2.selected_options if opt in item.options),
                    parameters=self.parameters,
                    parameters_addon1=self.addon1.parameters,
                    parameters_addon2=(self.addon2.parameters if self.addon2 == item else None))
    
    
    @property
    def total(self):
        return lib.AsyncTk().forward("get_total", 
                self,
                self.addon1,
                self.addon2)
    

    def _str(self, receipt=False):
        cls = type(self)
        lines = list()
        if receipt:
            lines.append((line_fmt(self.name, self.price), receipt_printer_style["item"]))
            lines.extend((f"    + {option}", NULL_DICT) for option in self.selected_options)
        else:
            lines.append((line_fmt(self.name, self.price)))
            lines.extend(f"    + {option}" for option in self.selected_options)
        addon1, addon2 = list(self.addon1), list(self.addon2)
        if self.category in cls.two_sides       \
                or self.category in cls.no_addons:
            addon1[2] = addon2[2] = 0 # set multiplier
        if self.category in cls.include_sides:
            for addon in (addon1, addon2):
                if addon[0] == "Sides":
                    addon[2] = 0
        if self.category in cls.include_drinks:
            for addon in (addon1, addon2):
                if addon[0] == "Drinks":
                    addon[2] = 0
        if self.addon1.name:
            if receipt:
                lines.append((line_fmt("  " + self.addon1.name, 
                        self.addon1.total * bool(addon1[2])), receipt_printer_style["item"]))
                lines.extend((f"    + {option}", NULL_DICT) for option in self.addon1.selected_options)
            else:
                lines.append(line_fmt("  " + self.addon1.name, self.addon1.price * bool(addon1[2])))
                lines.extend([f"    + {option}" for option in self.addon1.selected_options])    
        if self.addon2.name:
            if receipt:
                lines.append((line_fmt("  " + self.addon2.name,
                        self.addon2.total * bool(addon2[2])), receipt_printer_style["item"])) 
                lines.extend((f"    + {option}", NULL_DICT) for option in self.addon2.selected_options)
            else:
                lines.append(line_fmt("  " + self.addon2.name, self.addon2.price * bool(addon2[2])))
                lines.extend([f"    + {option}" for option in self.addon2.selected_options])
        if receipt:
            lines.append(("\n", NULL_DICT)) # need a newline to start printing
        else:
            lines.append("\n")
        return lines


    def __str__(self):
        return "\n".join(self._str())

    def receipt(self) -> str:
        return self._str(receipt=True)
 
    _param_init = lambda item: {
        "register":item.category in Order.register,
        "status":None
        }


class Order(collections.UserList, metaclass=lib.OrdersType):

    def __init__(self, initlist=None):
        super().__init__(initlist)
        self.taxrate = type(self).taxrate
        self.mode = ORDER_SELECT

    def __call__(self, item, addon1, addon2, idx=0):
        ModeController().reset()
        self.append(ItemTicket(item, addon1, addon2))
        ModeController().soft_select(len(Order())-1, idx)
        
    def set_item(self, item):
        assert Order().mode == ORDER_EDIT        
        index, subindex = ModeController().index, ModeController().subindex
        self.set(index, subindex, item)
        ModeController().unset()

    def pop(self, i=-1):
        ModeController().unselect()
        super().pop(i)
    
    def get(self, index, subindex):
        return self.data[index].get(subindex)
    
    def set(self, index, subindex, value):
        self.data[index] = self.data[index].set(subindex, value)

    def __str__(self):
        return "".join(str(ticket) for ticket in self.data)

    _param_init = lambda item, register: {
        "register":item.category in register,
        "status":None
        }
    
    printer_style = {
        "ticket_no": {
            "justify":bytes('C', "utf-8"),
            "size": bytes('L', "utf-8"),
        },

        "item": {
            "size": bytes('S', "utf-8"),
        },
        "total": {
            "justify":bytes('L', "utf-8"),
            "size": bytes('S', "utf-8"),
        },
    }


class ModeController(collections.UserList, metaclass=lib.SingletonType):

    def __init__(self, tabframe=None):
        super().__init__()
        assert tabframe is not None
        self.tabframe = tabframe
        self.mode = ORDER_SELECT
        self.tab_selector = {
            # default | two sides | no addons
            1:["Sides", "Sides",    None],
            2:["Drinks","Sides",    None]
        }        
        self.counter = 0
        self.case = 0
        self.current_order_len = 0
        self.index = None
        self.subindex = None
        self.selected_widget = None
        self.selected_widget = None
    
    @lib.update
    def update(self):
        size = len(Order())
        if self.current_order_len != size:
            self.current_order_len = size
            self.reset()

        # make sure main course items are not set as addon
        for i, ticket in enumerate(Order()):
            if ticket.addon1.category and ticket.addon1.category not in Order.no_addons:
                lib.AsyncTk().forward("stdout").info(f"Invalid addon ({ticket.addon1.name}) selected for '{ticket.name}'")
                Order()[i] = ticket.set(1, lib.NULL_MENU_ITEM)
                self.rewind()

            if ticket.addon2.category and ticket.addon2.category not in Order.no_addons:
                lib.AsyncTk().forward("stdout").info(f"Invalid addon ({ticket.addon2.name}) selected for '{ticket.name}'")
                Order()[i] = ticket.set(2, lib.NULL_MENU_ITEM)
                self.rewind()

    def rewind(self):
        if self.counter and self.mode == ORDER_SELECT:
            self._lift(self.counter)
            self.counter -= 1
            self._highlight_last_added(self.counter - 2)

    def reset(self):
        self.counter = 0
        self.case = 0
        
    def get_case(self, item):
        if item.category in Order.two_sides:
            return 1
        elif item.category in Order.no_addons:
            return 2
        else:
            return 0

    def unselect(self):
        self.mode = ORDER_SELECT
        self.index = None
        self.subindex = None
        self.reset()
        for widget in self:
            widget.remove_highlight()

    def _item_select_add(self, item=lib.NULL_MENU_ITEM):
        if self.counter == 0:
            result = self._add_ticket(item)
            self.case = self.get_case(item)
            if self.case == 2:
                self._highlight_last_added()
                if item.options:
                    EditOptions(lib.AsyncTk(), result)
                return
                    
        
        self._add_to_ticket(item)
        self._highlight_last_added()
        self._lift(self.counter + 1)
        self.counter += 1
        if self.counter == 3 and Order():
            self.counter = 0
            GroupEditOptions(lib.AsyncTk(), Order()[-1])

    def _item_edit_add(self, item):
        if self.index == len(Order()) - 1:
            self.counter = 0
        Order().set(self.index, self.subindex, item)
        self.selected_widget.event_generate("<FocusOut>")               

    @property
    def add_item(self):
        return self._item_select_add if self.mode == ORDER_SELECT else self._item_edit_add

    def select(self, index, subindex):
        self.mode = ORDER_EDIT
        self.index = index
        self.subindex = subindex
        self.selected_widget = self[index * 3 + subindex]

    def _lift(self, i):
        if i < 3:
            category = self.tab_selector[i][self.case]
            self.tabframe.select(category)
    
    def _highlight_last_added(self, offset=0):
        for widget in self:
            widget.remove_highlight()
        self[((len(Order()) - 1) * 3) + self.counter + offset].highlight()

    def _add_ticket(self, item):
        result = ItemTicket(item, lib.NULL_MENU_ITEM, lib.NULL_MENU_ITEM)
        Order().append(result)
        self.current_order_len += 1
        assert len(Order()) == self.current_order_len
        return result

    def _add_to_ticket(self, item):
        Order().set(-1, self.counter, item)
        
    
    
receipt_printer_style = Order.printer_style
MAX_WIDTH = 32
NULL_DICT = {}

def line_fmt(name, price):
    price = "$ {:.2f}".format(price / 100)
    n_space = MAX_WIDTH - len(name) - len(price)
    if n_space < 0:
        ...
    return name + (n_space * " ") + price


def NewOrder():
    return Order().clear()

