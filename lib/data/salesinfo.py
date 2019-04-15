from datetime import datetime
import csv


class SalesInfo:

    headers = ["timestamp", "total", "subtotal", "tax", "payment type", "items"]

    def __init__(self, filename):
        self.filename = filename
        
    def to_csv(self, data):
        timestamp = int(datetime.timestamp(datetime.now()))
        total = data["total"]
        subtotal = data["subtotal"]
        tax = data["tax"]
        items = data["items"]
        payment_type = data["payment_type"]
        return timestamp, total, subtotal, tax, payment_type, items
    
    def write(self, data):
        with open(self.filename, "a") as fp:
            writer = csv.writer(fp)
            writer.writerow(self.to_csv(data))
    
    def data(self):
        """returns a list of all items ordered"""
        with open(self.filename, "a") as fp:
            reader = csv.reader(fp)
            return [eval(row[4]) for row in reader]