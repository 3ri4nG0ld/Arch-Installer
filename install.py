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

		#Añade permisos al grupo sudo
		os.system("echo '%sudo ALL=(ALL) ALL' > /mnt/etc/sudoers.d/sudo")




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
		#os.system("pacman --noconfirm -S wget")

		os.system("arch-chroot /mnt pacman --noconfirm -S zsh zsh-syntax-highlighting zsh-autosuggestions fzf bat lsd")
		#os.system("arch-chroot /mnt mkdir /usr/share/zsh-syntax-highlighting")
		#os.system("cd /mnt/usr/share/zsh-syntax-highlighting && wget https://raw.githubusercontent.com/zsh-users/zsh-syntax-highlighting/master/zsh-syntax-highlighting.zsh")
			




		# Configurar zsh como shell por defecto 
		os.system("cp configs/useradd /mnt/etc/default/useradd")
		os.system("cp configs/skel/.zshrc /mnt/root/.zshrc")# copia la configuracion para root
		os.system("arch-chroot /mnt chsh -s /usr/bin/zsh")#Establezer zsh para root

		# Instalar carpeta skel configurada
		os.system("rm -rf /mnt/etc/skel")
		os.system("cp -r configs/skel/ /mnt/etc/")

		#Instalar scripts genericos
		os.system("sudo chmod +x scripts/genericos/*")
		os.system("sudo cp scripts/genericos/* /mnt/usr/bin/")

		# Instalar configuracion fzf
		os.system("sudo mkdir /mnt/etc/fzf")
		os.system("sudo cp configs/fzf.zsh /mnt/etc/fzf/fzf.zsh")
		os.system("sudo chmod 555 /mnt/etc/fzf/fzf.zsh")


		

		os.system("clear")

		while True:
			print("Desea Instalar un Escritorio?? (y/n)")
			opt_de = input("> ")
			if ((opt_de=="y") or (opt_de == "Y") or (opt_de == "yes") or (opt_de == "YES")):
				os.system("clear")
				print("Que escritorio quieres instalar??")
				print("1.- BSPWM")
				print("2.- XFCE4")
				opt_de_type = input("> ")
				if (opt_de_type == "1"):
					print("Instalar BSPWM") # introducir qui codigo instalacion BSPWM

					#Instala las dependencias y el escritorio
					os.system("arch-chroot /mnt pacman --noconfirm -S xorg-server xorg-xinit picom rofi mesa mesa-demos feh libxcb xcb-util xcb-util-wm xcb-util-keysyms bspwm sxhkd qterminal ttf-fira-code git")

					os.system("clear")
					print("Elije drivers graficos: ")
					print("1.- INTEL")
					print("2.- AMD")
					print("3.- NVIDIA")
					print("4.- VMware")

					opt=input("> ")
					if(opt == "1"):
						os.system("arch-chroot /mnt pacman --noconfirm -S xf86-video-intel intel-ucode")

					elif(opt == "2"):
						os.system("arch-chroot /mnt pacman --noconfirm -S xf86-video-amdgpu amd-ucode")

					elif(opt == "3"):
						print("Propietarios o Libres??")
						print("1.- Propietarios (* desarrollados por NVIDIA)")
						print("2.- Libres (* de codigo abierto)")
						opt=input("> ")
						if(opt == "1"):
							os.system("arch-chroot /mnt pacman --noconfirm -S nvidia nvidia-utils")
						elif(opt == "2"):
							os.system("arch-chroot /mnt pacman --noconfirm -S xf86-video-nouveau")

					elif(opt == "4"):
						os.system("arch-chroot /mnt pacman --noconfirm -S open-vm-tools xf86-input-vmmouse xf86-video-vmware")

					os.system("clear")
					print("Desea instalar LigthDM??(y/n)")
					opt=input("> ")
					if ((opt=="y") or (opt == "Y") or (opt == "yes") or (opt == "YES")):
						os.system("arch-chroot /mnt pacman --noconfirm -S ligthdm")
					elif ((opt == "N") or (opt == "n") or (opt == "no") or (opt == "NO")):
						os.system("echo -e 'sxhkd &\nexec bspwm' > /mnt/etc/skel/.xinitrc")

		







			

					#instalar cuentes
					os.system("mkdir /mnt/usr/local/share/fonts/")
					os.system("sudo cp fonts/* /mnt/usr/local/share/fonts/")
					os.system("sudo chmod 555 /mnt/usr/local/share/fonts/*")

					#install 
					#os.system("cd /mnt/tmp && git clone https://github.com/baskerville/bspwm.git && cd bspwm && arch-chroot /mnt make && arch-chroot /mnt sudo make install")
					#os.system("cd /mnt/tmp && git clone https://github.com/baskerville/sxhkd.git && cd sxhkd && arch-chroot /mnt make && arch-chroot /mnt sudo make install")


				elif (opt_de_type == "2"):
					print("Instalar XFCE4") # introducir qui codigo instalacion XFCE4
				print("quieres instalar otro escritorio??(y/N)")
				opt = input("> ")
				if ((opt=="y") or (opt == "Y") or (opt == "yes") or (opt == "YES")):
					pass
				elif ((opt == "") or (opt == "N") or (opt == "n") or (opt == "no") or (opt == "NO")):
					break
			elif ((opt_de == "N") or (opt_de == "n") or (opt_de == "no") or (opt_de == "NO")):
				break
			else:
				pass


		os.system("clear")
		# Crear un usuario principal
		while True:
			print("Desea Crear un usuario principal?? (Y/n)")
			print("* Con permisos de sudo")
			opt = input("> ")
			if ((opt=="y") or (opt == "Y") or (opt == "yes") or (opt == "YES")):
				os.system("clear")
				print("Introduce Tu nombre de usuario (* solo minusculas)")
				username = input("Usuario: ")
				os.system("clear")
				print("Escribe Tu nombre completo")
				full_name = input("Nombre Completo: ")
				username=username.lower()
				os.system(f"arch-chroot /mnt useradd -m {username} -c '{full_name}' -G sudo")
				os.system(f"arch-chroot /mnt passwd {username}")
				os.system("clear")
				os.system("modprobe ecryptfs")
				os.system("clear")
				print("Introduzca la contraseña para cifrar carpeta del usuario: ")
				os.system(f"arch-chroot /mnt ecryptfs-migrate-home --user '{username}'") # Cifra la carpeta del usuario principal (--nopwcheck no funciona)
				os.system(f"rm -rf /mnt/home/{username}.*")
				os.system("rm -rf /mnt/etc/pam.d/system-auth")
				os.system("cp configs/system-auth /mnt/etc/pam.d/system-auth")
				break
			elif (opt == "N" or opt == "n" or opt == "no" or opt == "NO"):
				break
			else:
				pass

		#instalar YAY
		os.system("useradd -m yayuser -G sudo")# crea un usuario pa la instalacion
		os.system("arch-chroot /mnt pacman --noconfirm -S fakeroot go")
		os.system("arch-chroot /mnt pacman -S --noconfirm --needed git base-devel")

		os.system(f"git clone https://aur.archlinux.org/yay.git /mnt/home/yay")
		os.system("sudo chmod 777 /mnt/home/yay")
		os.system(f"arch-chroot /mnt su yayuser -c 'cd /home/yay && makepkg /home/yay -si'")

		#instalar polybar
		if (((opt_de=="y") or (opt_de == "Y") or (opt_de == "yes") or (opt_de == "YES")) and (opt_de_type == "1")):
			os.system("arch-chroot /mnt yay -Sy polybar")


		

	os.system("loadkeys es") # Carga el teclado en Español
	# if ls /sys/firmware/efi/efivars == true --> Modo UEFI --> else =  Modo BIOS
	os.system("timedatectl set-ntp true") # Sincroniza hora del reloj
	os.system("pacman -Sy")
	os.system("clear")

	print("""Porfavor seleccione el modo de particionado del disco:
		1.- Estandar (Todo en una partición sin cifrar)
		2.- LVM Cifrado (Crea una particion cifrada y dentro unidades logicas LVM)""")
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