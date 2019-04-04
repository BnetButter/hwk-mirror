from lib import POSInterface
import logging
import sys

logger = logging.getLogger(__name__)
stream_handler = logging.StreamHandler(stream=sys.stderr)
stream_handler.setFormatter(logging.Formatter("%(levelname)s - %(funcName)s - %(message)s"))
logger.addHandler(stream_handler)

class POSProtocolBase:

    def __init__(self):
        logger.warning(f"{type(self).__name__} delegate does not implement any methods")

    def get_connection_status(self, *args, **kwargs):
        logger.warning("NotImplemented")
        raise NotImplementedError

    def global_shutdown(self, *args, **kwargs):
        logger.warning("NotImplemented")
        raise NotImplementedError
    
    def get_time(self, *args, **kwargs):
        logger.warning("NotImplemented")
        raise NotImplementedError
     
    def get_ticket_no(self, *args, **kwargs):
        logger.warning("NotImplemented")
        raise NotImplementedError

    def new_order(self, *args, **kwargs):
        logger.warning("NotImplemented")
        raise NotImplementedError
        
    def edit_order(self, *args, **kwargs):
        logger.warning("NotImplemented")
        raise NotImplementedError

    def cancel_order(self, *args, **kwargs):
        logger.warning("NotImplemented")
        raise NotImplementedError

    def get_order_status(self, *args, **kwargs):
        logger.warning("NotImplemented")
        raise NotImplementedError

