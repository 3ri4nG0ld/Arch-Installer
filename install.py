#!/usr/bin/env python3

import os





def instalar_sistema_base():


	#----- Funciones para el particionado -------#
	def particionado_estandar():
		os.system("lsblk -p")
		print("Indique el disco donde quiere realizar el particionado:")
		disk = input("> ")
		os.system("clear")
		print("Porfavor realize 2 particiones gpt:\n\n- Partición 1 - 512MB - EFI System\n- Partición 2 - [Tamaño maximo] - Linux filesystem\n\n* Puedes investigar como realizar particiones en cfdisk")		
		input("Pulse enter para continuar...")
		os.system("cfdisk " + disk)
		print("Porfavor indique la particion 1 - EFI System")
		part_efi = input("> ")
		print("Porfavor indique la particion 2 - Linux filesystem")
		part_system = input("> ")
		os.system("mkfs.ext4 " + part_system)
		os.system("mkfs.fat " + part_efi)
		os.system("mount " + part_system + " /mnt")
		os.system("mkdir /mnt/efi")
		os.system("mount " + part_efi + " /mnt/efi")
	def particionado_cifrado():
		pass
	def particionado_lvm_cifrado(hostname):
	#--------------------------------------------#
	#----- Funciones de instalación -------------#
	def instalar_sistema_y_efi():
		os.system("pacstrap /mnt base linux linux-firmware")




	os.system("loadkeys es") # Carga el teclado en Español
	# if ls /sys/firmware/efi/efivars == true --> Modo UEFI --> else =  Modo BIOS
	os.system("timedatectl set-ntp true") # Sincroniza hora del reloj
	os.system("pacman -Sy")
	os.system("clear")
	print("Porfavor indique el hostname del equipo:")
	hostname = input(">")

	print("""Porfavor seleccione el modo de particionado del disco:
		1.- Estandar (Todo en una partición sin cifrar)
		2.- Estandar cifrado (Todo en una partición cifrada)
		3.- LVM Cifrado (Crea una particion cifrada y dentro unidades logicas LVM)

		4.- Estandar + separar particion home (Separa la carpeta de los usuarios a otro disco)""")
	opt=input("> ")

	if (opt == "1"):
		print("Instalacion estandar")
		particionado_estandar()
		instalar_sistema_y_efi()
	elif (opt == "2"):
		print("Instalacion estandar cifrado")

instalar_sistema_base()