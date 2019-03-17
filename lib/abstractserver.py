from abc import ABCMeta
from abc import abstractmethod

class abstract_server(metaclass=ABCMeta):
    
    @abstractmethod
    def ping_client(self):
        pass
    
    @abstractmethod
    def send_global_shutdown(self):
        pass
    
    @abstractmethod
    def send_time(self):
        pass
    
    @abstractmethod
    def send_menu(self):
        pass
    
    @abstractmethod
    def send_ticket_no(self):
        pass
    
    @abstractmethod
    def respond_new_order(self):
        pass
    
    @abstractmethod
    def respond_edit_order(self):
        pass
    
    @abstractmethod
    def respond_cancel_order(self):
        pass
    
    @abstractmethod
    def send_queue(self):
        pass
    
    @abstractmethod
    def send_order_status(self):
        pass

class abstract_client(metaclass=ABCMeta):
    
    @abstractmethod
    def get_connection_status(self):
        pass
    
    @abstractmethod
    def global_shutdown(self):
        pass
        
    @abstractmethod
    def ping_respond(self):
        pass

    @abstractmethod
    def get_time(self):
        pass 

class abstract_pos_client(abstract_client, metaclass=ABCMeta):

    @abstractmethod
    def get_ticket_no(self):
        pass
    
    @abstractmethod
    def new_order(self):
        pass
    
    @abstractmethod
    def edit_order(self):
        pass
    
    @abstractmethod
    def cancel_order(self):
        pass
    
    @abstractmethod
    def get_order_status(self):
        pass
    
class abstract_display_client(abstract_client ,metaclass=ABCMeta):

    @abstractmethod
    def request_menu(self):
        pass

    @abstractmethod
    def get_queue(self):
        pass
    
    @abstractmethod
    def update_order_status(self):
        pass
    
    @abstractmethod
    def reply_cancel_request(self):
        pass
    
    @abstractmethod
    def ping_respond(self):
        pass