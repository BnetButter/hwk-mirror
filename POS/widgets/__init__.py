from tkinter import ttk
from lib import TabbedFrame
from lib import MenuWidget
from lib import stdout
from lib import ReinstanceType
from .menu_display import *
from .console import *
from .order_display import *
from .menu_editor import *
from .price_display import PriceDisplay
from .checkout_display import *
from .network_status import NetworkStatus
from .titlebar import *
from .progress_tab import *
from .order import Order, NewOrder
from .control_panel import *


class OrderDisplay(TabbedFrame, metaclass=ReinstanceType, device="POS"):
    tabfont = ("Courier", 14)
    
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.style.configure("OrderDisplay.TNotebook.Tab",
            font=self.tabfont,
            width=10,
            padding=5)
        self._notebook.configure(style="OrderDisplay.TNotebook")
        order_frame = OrdersFrame(self)
        checkout_frame = CheckoutFrame(self)
        progress_frame = ProgressFrame(self)
    
        self["Orders"] = order_frame
        self["Checkout"] = checkout_frame
        self["Processing"] = progress_frame

        checkout_frame.set_keypress_bind(self, "Checkout", on_enter=checkout_frame.on_enter)
        # alias for lib.PriceInput.set_keypress_bind
        progress_frame.set_keypress_bind(lib.AsyncTk(),
                condition=progress_frame.keybind_condition(self, "Processing"),
                on_enter=progress_frame.on_enter)


    def ctor(self):
        self.update()
    
    def dtor(self):
        for task in self.update_tasks:
            lib.AsyncTk().remove(task)

    def update(self):
        self.update_tasks = (self["Orders"].update_order_list(),
        self["Checkout"].update_order_list(),
        self["Processing"].update_order_status())


class MenuDisplay(TabbedFrame, metaclass=ReinstanceType, device="POS"):
    tabfont = ("Courier", 14)
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.style.configure("MenuDisplay.TNotebook.Tab",
                font=self.tabfont,
                padding=5)
        self.navigator = OrderNavigator(parent=self)
        self.navigator.update()
        self._notebook.configure(style="MenuDisplay.TNotebook")
        for category in MenuDisplay.categories:
            self[category] = CategoryFrame(self, category)
            self[category].set_keypress_bind(lib.AsyncTk(), MenuDisplay, OrderDisplay, "Orders")
            self[category].set_item_command(OrderDisplay)
    
    def set_keypress_bind(self, orderdisplay):
        for frame in self.data.values():
            frame.set_keypress_bind(lib.AsyncTk(), self, orderdisplay, "Orders")

class Console(TabbedFrame, metaclass=WidgetType, device="POS"):
    tabfont = ("Courier", 10)
    instance = None

    def __init__(self, parent, **kwargs):
        super().__init__(parent, "stdout", "stderr", "control panel", **kwargs)
        style = ttk.Style(self)
        style.configure("TNotebook.Tab", font=self.tabfont, padding=1)
        style.configure("TNotebook", padding=-1)

        stdout_scrollbar = tk.Scrollbar(self["stdout"])
        stderr_scrollbar = tk.Scrollbar(self["stderr"])
        
        stdout_textbox = console_stdout(self["stdout"],
                yscrollcommand=stdout_scrollbar.set)
        stderr_textbox = console_stderr(self["stderr"], 
                yscrollcommand=stderr_scrollbar.set)

        stdout_scrollbar["command"] = stdout_textbox.yview
        stderr_scrollbar["command"] = stderr_textbox.yview

        self["stdout"].grid_columnconfigure(0, weight=1)
        self["stderr"].grid_columnconfigure(0, weight=1)

        stdout_textbox.grid(row=0, column=0, sticky="nswe")
        stderr_textbox.grid(row=0, column=0, sticky="nswe")
        stdout_scrollbar.grid(row=0, column=1, sticky="nse")
        stderr_scrollbar.grid(row=0, column=1, sticky="nse")
    
        controlpanel = ControlPanel(self["control panel"])
        controlpanel.add_mode_toggle(MenuDisplay, MenuEditor)
        controlpanel.add_invoice_printer()
        controlpanel.grid(sticky="nswe", pady=2, padx=2)
        type(self).instance = self


class MenuEditor(tk.Frame, metaclass=ReinstanceType, device="POS"):
    font=("Courier", 14)

    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.keyboard = lib.Keyboard(self, bd=2, relief=tk.RAISED)
        PriceEntry.keyboard = self.keyboard
        self.category_editor = MenuEditorTabs(self)
        self.category_config = {
                    category:ConfigFrame(self, category, font=self.font, bd=2, relief=tk.SUNKEN)
                    for category in type(self).categories}

        self.controls = ButtonFrame(self, font=self.font, bd=2, relief=tk.RIDGE)
        self.item_adder = ItemAdder(self, self.keyboard, font=self.font, bd=2, relief=tk.SUNKEN)
        self.item_adder.add_item.command = self.on_add_item

        self.category_editor.grid(row=0, column=0, rowspan=2, sticky="nswe")
        self.item_adder.grid(row=2, column=0, sticky="nswe")
        self.keyboard.grid(row=3, column=0, columnspan=2, sticky="nswe")
        self.controls.grid(row=0, column=1, sticky="swe", padx=5, pady=5)
        for widget in self.category_config.values():
            widget.grid(row=1, column=1, rowspan=2, sticky="swe")

        self.controls.save.command = self.on_save
        self.controls.apply.command = self.on_apply
        self.controls.reset.command = self.on_reset

    def ctor(self):
        self.update()

    def dtor(self):
        lib.AsyncTk().remove(self.update_task)

    def update(self):
        @lib.update
        def update():
            # remove empty tab
            for category in self.category_editor.data:
                frame = self.category_editor[category]
                if frame.is_empty():
                    self.category_editor.pop(category).destroy()
                    self.category_config.pop(category).destroy()
                    return # next line will raise error since the frame is gone

            category = self.category_editor.current()
            self.item_adder.category = category
            for widget in self.category_config.values():
                widget.update(category)
        self.update_task = update()

    def on_add_item(self, *args):
        result = self.item_adder.get()
        category = result[0]
        if category in self.category_editor.data:
            self.category_editor[category].add_item(*result)
        else:
            new_category = EditorCategoryFrame(self, category)
            new_config = ConfigFrame(self, category, font=self.font)
        
            new_category.add_item(*result)
            new_config.grid(row=1, column=1, rowspan=2, sticky="swe")
            self.category_editor[category] = new_category
            self.category_config[category] = new_config

        self.item_adder.clear()
        self.category_editor.select(category)

    def on_apply(self, *args):
        messages = [config.apply().strip() for config in self.category_config.values()]
        messages.append(self.category_editor.apply().strip())
        messages = "\n".join(message for message in messages if message).strip()
        if messages:
            logging.getLogger("main.POS.gui.stdout").info(messages)
        
        EditorDelegate().apply()        
        # QoL: lift console stdout tab
        Console.instance.select("stdout")
        ReinstanceType.reinstance()
        self.on_reset()

    def on_save(self, *args):
        messages = [config.apply().strip() for config in self.category_config.values()]
        messages.append(self.category_editor.apply().strip())
        messages = "\n".join(message for message in messages if message).strip()
        if messages:
            logging.getLogger("main.POS.gui.stdout").info(messages)
        AsyncTk().forward("edit_menu", EditorDelegate().apply())
        Console.instance.select("stdout")
        ReinstanceType.reinstance()
        self.on_reset()
        
    def on_reset(self, *args):
        EditorDelegate().reset()
        ReinstanceType.reinstance(type(self))


            



        