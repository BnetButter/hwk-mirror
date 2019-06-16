#! /bin/bash

autostart=$HOME/.config/lxsession/LXDE/autostart
device=$*
newline="\n"
PYTHON=$HOME/.local/bin/python3.7

cd $HOME
pwd
git clone https://github.com/BnetButter/hwk

cd $HOME/hwk/Printer
pwd
echo "running setup for hwk/Printer"
$PYTHON setup.py install

cd $HOME/hwk/CashDrawer/module
pwd
echo "running setup for hwk/CashDrawer"
$PYTHON setup.py install

cd $HOME/hwk/GoogleDrive
pwd
echo "running setup for hwk/GoogleDrive"
$PYTHON setup.py install

if [ "$device" = "pos" ]
then
    lx_script="@/home/pi/hwk/start_pos.py"
elif [ "$device" = "display" ]
then
    lx_script="@/home/pi/hwk/start_display.py"
else
    echo error no device input
    exit
fi

echo selected "$lx_script"

if grep -q $lx_script $autostart
then
    echo "no need to update autostart"
    echo "setup complete"
    exit
else
    (echo ""; echo $lx_script) >> $autostart
    echo "updated autostart"
fi
echo "setup complete"
exit