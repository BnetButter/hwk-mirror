"""Modified Epsilon-Interface Cash Drawer
Currently it does not support open/close check."""
from lib import DEBUG

if DEBUG: 
    # can't build extension on x86 arch
    # so we must provide a dummy function and object.
    class Drawer:
        """instance a cash drawer object"""
        def open(self):
            print("opening cash drawer...")

else:
    import _cashdrawer
    # aliases type.__call__
    def Drawer() -> object:
        """instance a cash drawer object"""
        self = _cashdrawer.new()
        self.__init__()
        return self