#!/usr/bin/env python3

import os
from getpass import getpass



def instalar_sistema_base():


	#----- Funciones para el particionado -------#
	def particionado_estandar():
		#--------------------------------------#
		# Esta funcion sirve para crear el particionado del disco sin cifrar
		os.system("lsblk -p")
		print("Indique el disco donde quiere realizar el particionado:")
		disk = input("> ")
		os.system(f"parted -s {disk} mklabel gpt") # Crea tabla de particiones GPT
		os.system(f"parted -s {disk} mkpart efi fat32 0 512") # Crea una particion llamada efi de 512M
		os.system(f"parted -s {disk} mkpart system ext4 512 100%") # Crea una partición llamada system con el resto del almacenamiento
		os.system("clear")
		print("Indicar particiones manualmente?(y/N)")
		print("* Opcional")
		opt=input("> ")
		if((opt =="y") or (opt == "Y")):
			part_efi=input("Particion EFI: ")
			part_system=input("Particion System: ")
			part_home=input("* Particion Home: ")
			if(part_home):
				print("Se utilizara disco externo")
		elif ((opt == "") or (opt == "N") or (opt == "n")):
			part_efi=disk+"1"
			part_system=disk+"2"


		os.system("mkfs.ext4 " + part_system)
		os.system("mkfs.fat " + part_efi)
		os.system("mount " + part_system + " /mnt")
		os.system("mkdir /mnt/boot")
		os.system("mkdir /mnt/boot/efi")
		os.system("mount " + part_efi + " /mnt/boot/efi")
	def particionado_lvm_cifrado():
		os.system("lsblk -p")
		print("Indique el disco donde quiere realizar el particionado:")
		disk = input("> ")
		os.system(f"parted -s {disk} mklabel gpt") # Crea tabla de particiones GPT
		os.system(f"parted -s {disk} mkpart efi fat32 0 512") # Crea una particion llamada efi de 512M
		os.system(f"parted -s {disk} mkpart boot fat32 512 1024")
		os.system(f"parted -s {disk} mkpart system ext4 1024 100%") # Crea una partición llamada system con el resto del almacenamiento



		os.system("clear")
		print("Indicar particiones manualmente?(y/N)")
		print("* Opcional")

		opt=input("> ")
		if((opt =="y") or (opt == "Y")):
			part_efi=input("Particion EFI: ")
			part_boot=input("Particion Boot: ")
			part_system=input("Particion System: ")
			part_home=input("* Particion Home: ")
			if(part_home):
				print("Se utilizara disco externo")
		elif ((opt == "") or (opt == "N") or (opt == "n")):
			part_efi=disk+"1"
			part_boot=disk+"2"
			part_system=disk+"3"




		os.system("clear")
		# Solicita la password para cifrar la particion principal
		while True:
			print("Por favor introduce la contraseña de cifrado: ")
			passwd = getpass("Password: ")
			passwd2 = getpass("Repeat Password: ")
			if (passwd == passwd2):
				break
			else:
				os.system("clear")
				print("Las contraseñas no coinciden")

		#Encripta la particion principal
		os.system("echo -n " + passwd + " | cryptsetup luksFormat --type luks2 "+ part_system + " -d -")
		os.system("echo -n " + passwd + " | cryptsetup open " + part_system + " enc -d -")

		#Crea el volumen logico
		os.system("pvcreate --dataalignment 1m /dev/mapper/enc")
		os.system("vgcreate vol /dev/mapper/enc")
		os.system("lvcreate -l +100%FREE vol -n root")
		

		#Formatear particiones
		os.system("mkfs.fat -F32 " + part_efi)
		os.system("mkfs.ext4 " + part_boot)
		os.system("mkfs.ext4 /dev/mapper/vol-root")
		


		#montar particiones
		os.system("mount /dev/mapper/vol-root /mnt")
		os.system("mkdir /mnt/boot/")
		os.system("mount " + part_boot + " /mnt/boot")

		#Generar fstab
		os.system("genfstab -U -p /mnt >> /mnt/etc/fstab")

		#Instalar sistema base
		os.system("pacstrap /mnt base linux lvm2")

		#Edita el archivo /etc/mkinitcpio.conf
		file=open("/mnt/etc/mkinitcpio.conf","r")
		text=file.read()
		text=text.replace("HOOKS=(base udev autodetect modconf block filesystems keyboard fsck)","HOOKS=(base udev autodetect modconf block encrypt lvm2 filesystems keyboard fsck)")
		file.close()
		file=open("/mnt/etc/mkinitcpio.conf","w")
		file.write(text)
		file.close()
		# Aplica la configuracion
		os.system("arch-chroot /mnt mkinitcpio -p linux")

		# Instala el Grub
		os.system("arch-chroot /mnt pacman --noconfirm -S grub efibootmgr")
		# Edita el archivo /etc/default/grub
		file=open("/mnt/etc/default/grub","r")
		text=file.read()
		text=text.replace('GRUB_CMDLINE_LINUX_DEFAULT="loglevel=3 quiet"','GRUB_CMDLINE_LINUX_DEFAULT="loglevel=3 cryptdevice=' + part_system + ':vol:allow-discards quiet"')
		text=text.replace('#GRUB_ENABLE_CRYPTODISK=y','GRUB_ENABLE_CRYPTODISK=y')
		file.close()
		file=open("/mnt/etc/default/grub","w")
		file.write(text)
		file.close()

		#Montar EFI
		os.system("mkdir /mnt/boot/EFI")
		os.system("mount " + part_efi + " /mnt/boot/EFI")

		#Instalar y aplicar configuración grub
		os.system("arch-chroot /mnt grub-install --target=x86_64-efi --bootloader-id=ArchLinux --recheck")
		os.system("arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg")

		
		return part_system
	#--------------------------------------------#
	#----- Funciones de instalación -------------#
	def instalar_sistema_y_efi():
		os.system("pacstrap /mnt base linux linux-firmware")
		os.system("genfstab -U /mnt >> /mnt/etc/fstab")
		os.system("arch-chroot /mnt pacman --noconfirm -S grub efibootmgr")
		os.system("arch-chroot /mnt grub-install --target=x86_64-efi --bootloader-id=ArchLinux --recheck")
		os.system("arch-chroot /mnt grub-mkconfig -o /boot/grub/grub.cfg")
	def configuracion_basica():
		os.system("arch-chroot /mnt pacman --noconfirm -S sudo networkmanager ecryptfs-utils")
		os.system("arch-chroot /mnt systemctl enable NetworkManager")

		os.system("arch-chroot /mnt ln -sf /usr/share/zoneinfo/Europe/London /etc/localtime")
		os.system("arch-chroot /mnt hwclock --systohc")


		# Edita el idioma del sistema a español
		file=open("/mnt/etc/locale.gen","r")
		text=file.read()
		text=text.replace('#es_ES.UTF-8 UTF-8','es_ES.UTF-8 UTF-8')
		file.close()
		file=open("/mnt/etc/locale.gen","w")
		file.write(text)
		file.close()

		# Aplica la configuracion de idioma
		os.system("arch-chroot /mnt locale-gen")

		# Editar distribucion del teclado
		os.system("echo 'KEYMAP=es' > /mnt/etc/vconsole.conf")
		
		# Se aplica el hostname
		os.system("clear")
		print("Porfavor indique el hostname del equipo:")
		hostname = input("> ")
		os.system(f"echo {hostname} > /mnt/etc/hostname")
		os.system(f"echo '127.0.0.1	localhost\n::1	localhost\n127.0.0.1	{hostname}'> /etc/hosts")



		



		# Crea grupo sudo
		os.system("arch-chroot /mnt groupadd sudo")

		#edita el archivo sudoers para que el grupo sudo tenga todos los permisos
		file=open("/mnt/etc/sudoers","r")
		text=file.read()
		text=text.replace('# %sudo ALL=(ALL) ALL','%sudo ALL=(ALL) ALL')
		file.close()
		file=open("/mnt/etc/sudoers","w")
		file.write(text)
		file.close()





		os.system("clear")
		while True:
			print("Desea activar la contraseña de root?? (y/N)")
			opt = input("> ")
			if ((opt=="y") or (opt == "Y") or (opt == "yes") or (opt == "YES")):
				os.system("arch-chroot /mnt passwd root")
				break
			elif ((opt == "") or (opt == "N") or (opt == "n") or (opt == "no") or (opt == "NO")):
				break
			else:
				pass
		os.system("arch-chroot /mnt pacman --noconfirm -S rsync lsof which")
		os.system("clear")
		while True:
			print("Desea Crear un usuario principal?? (Y/n)")
			print("* Con permisos de sudo")
			opt = input("> ")
			if ((opt=="y") or (opt == "Y") or (opt == "yes") or (opt == "YES")):
				username = input("Usuario: ")
				while True:
					print("Por favor introduce la contraseña del usuario: ")
					passwd = getpass("Password: ")
					passwd2 = getpass("Repeat Password: ")
					if (passwd == passwd2):
						break
					else:
						os.system("clear")
						print("Las contraseñas no coinciden")

				os.system(f"arch-chroot /mnt useradd -m {username} -G sudo -p {passwd}")
				os.system(f"arch-chroot /mnt ecryptfs-migrate-home -u {username}")
				break
			elif (opt == "N" or opt == "n" or opt == "no" or opt == "NO"):
				break
			else:
				pass

		os.system("arch-chroot /mnt pacman --noconfirm -S htop screenfetch neofetch zsh")

	os.system("loadkeys es") # Carga el teclado en Español
	# if ls /sys/firmware/efi/efivars == true --> Modo UEFI --> else =  Modo BIOS
	os.system("timedatectl set-ntp true") # Sincroniza hora del reloj
	os.system("pacman -Sy")
	os.system("clear")

	print("""Porfavor seleccione el modo de particionado del disco:
		1.- Estandar (Todo en una partición sin cifrar)
		2.- LVM Cifrado (Crea una particion cifrada y dentro unidades logicas LVM)

		3.- Estandar + separar particion home (Separa la carpeta de los usuarios a otro disco)""")
	opt=input("> ")

	if (opt == "1"):
		print("Instalacion estandar")
		particionado_estandar()
		instalar_sistema_y_efi()
		configuracion_basica()
	elif (opt == "2"):
		print("Instalacion estandar cifrado")
		particionado_lvm_cifrado()
		#instalar_sistema_y_efi_lvm_cifrado(part_system)
		configuracion_basica()

instalar_sistema_base()
#os.system("umount -R /mnt")