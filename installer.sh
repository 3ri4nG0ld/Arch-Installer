#!/bin/sh
if [ "$(ping -c1 8.8.8.8)" ]
then sudo apt-get install python3 git -y && sudo chmod +x installer.py && sudo python3 installer.py
else echo -e "Es necesario una conexion a internet\nPorfavor compruebe su conexión"
fi