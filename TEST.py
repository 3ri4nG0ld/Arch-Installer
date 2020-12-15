file=open("test1.txt","r")

text=file.read()
text=text.replace("buenas","pepe")

file.close()
file=open("test1.txt","w")
file.write(text)