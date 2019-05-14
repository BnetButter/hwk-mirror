PYTHON =/home/bnetbutter/.env/hwk/bin/python3.7
ACTIVATE = /home/bnetbutter/.env/hwk/bin/activate


all: activate
	$(PYTHON) main.py pos

activate:
	/bin/bash $(ACTIVATE) hwk

kill:
	$(PYTHON) main.py kill