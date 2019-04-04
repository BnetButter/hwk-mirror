from abc import ABCMeta
from abc import abstractmethod
from .data import SYS_STDERR
import logging
import sys

logger = logging.getLogger(SYS_STDERR)

class abstract_server(metaclass=ABCMeta):
        
    @abstractmethod
    def global_shutdown(self):
        ...
    
    @abstractmethod
    def send_time(self):
        ...

    @abstractmethod
    def send_menu(self):
        ...

    @abstractmethod
    def send_ticket_no(self):
        ...
    
    @abstractmethod
    def respond_new_order(self):
        ...

    
    @abstractmethod
    def respond_edit_order(self):
        ...
        
    
    @abstractmethod
    def respond_cancel_order(self):
        ...
        
    
    @abstractmethod
    def send_queue(self):
        ...
    
    @abstractmethod
    def send_order_status(self):
        ...

class abstract_client(metaclass=ABCMeta):
    
    @abstractmethod
    def get_connection_status(self):
        ...
    
    @abstractmethod
    def global_shutdown(self):
        ...

    @abstractmethod
    def get_time(self):
        ...

class abstract_pos_client(abstract_client, metaclass=ABCMeta):

    @abstractmethod
    def get_ticket_no(self):
        ...
    
    @abstractmethod
    def new_order(self):
        ...
    
    @abstractmethod
    def edit_order(self):
        ...
    
    @abstractmethod
    def cancel_order(self):
        ...
    
    @abstractmethod
    def get_order_status(self):
        ...
    
class abstract_display_client(abstract_client ,metaclass=ABCMeta):

    @abstractmethod
    def request_menu(self):
        ...

    @abstractmethod
    def get_queue(self):
        ...
    
    @abstractmethod
    def update_order_status(self):
        ...
    
    @abstractmethod
    def reply_cancel_request(self):
        ...
    
    @abstractmethod
    def ping_respond(self):
        ...

