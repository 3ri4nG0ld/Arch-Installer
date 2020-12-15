from getpass import getpass
import sys,os

while True:
	passwd = getpass("Password: ")
	passwd2 = getpass("Repeat Password: ")
	if (passwd == passwd2):
		print("Acceso permitido")
		break
	else:
		os.system("clear")
		print("Las contraseñas no coinciden")


parted -s {device} mklabel gpt
parted -s {device} mkpart efi 0 512
parted -s {device} mkpart system 512 100%

