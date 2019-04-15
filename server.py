from Server import Server
def main(shutdown_system=False):
    try:
        server = Server()
        server.mainloop()
    except:
        print("Failed to run server as it may already be running")