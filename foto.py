#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# sorts images by date
 
import os, sys
from PIL import Image
import piexif
import shutil
from pathlib import Path
import hashlib

# задаём директорию для сортировки
#rootdir = os.getcwd()
#rootdir = "/storage/emulated/0/DCIM/Screenshots/"
rootdir = "/mnt/smb/FoTO/"
dirname = rootdir

##########
def image_sort(path, recur = 0):
    if not recur:
    	# если главная папка
    	print("   sorting started ...")
 
    # собирает все подпапки в список и рекурсивно обходит
    imagelist = []
 
    if os.path.isdir(path): # если папка
        for x in os.listdir(path):
            # имя файла с полным путём
            absx = os.path.join(path, x)
            # если файл, то добавляем в список
            if os.path.isfile(absx):
            	imagelist.append(absx) 
            else:
                print("summon subsort in %s"%x)
                image_sort(absx, recur=1)
        # проходит по содержимому папки/подпапки
        for fname in imagelist:
            try:
            	# получить разрешение
            	resolution = Image.open(fname).size
            	# получаем exif
            	kartinka = piexif.load(fname)
            	datetime = None
            except IOError:
            	# перенос в папку "0"
            	# moveit ->
            	mess = "seems not image: %s"%os.path.split(fname)[-1]
            	e = Path(fname)
            	#print(e.suffix)
            	if e.suffix == ".py":
            		#print(os.path.split(fname)[-1] + " file, skip.")
            		mess = mess + " file, scip."
            		print(mess)
            	elif e.suffix == ".ini" or e.suffix == ".db":
            		mess = mess + " delete."
            		print(mess)
            		os.remove(fname)
            	#elif e.suffix == ".mpg":
            	else:
            		i = 0
            		
            		imdir = os.path.join(rootdir, "0")
            		if not os.path.exists(imdir):
            			os.mkdir(imdir)
            		nfname = os.path.join(imdir,  os.path.split(fname)[-1])
            		compare(i, fname, nfname, nfname)
            	continue
            except Exception:
            	# exif отсутствует
            	datetime = "0000:00"
            else:
            	for i in ("0th", "Exif", "GPS", "1st"):
            		for tag in kartinka[i]:
            			# Нам нужны EXIF теги DateTime и DateTimeOriginal
            			if ((piexif.TAGS[i][tag]["name"] == "DateTime") or ((piexif.TAGS[i][tag]["name"] == "DateTimeOriginal"))):
            				datetime = kartinka[i][tag]
            	# если теги есть, но пустые			
            	if ( datetime == None ):
            		datetime = b'0000:00'			
            	datetime = datetime.decode("utf-8")
            	
            #print(fname)
            foldername = datetime[5:7] + "." + datetime[0:4]
            # папка назначения
            imdir = os.path.join(rootdir, foldername)
            # реальное название папки
            realdir = os.path.split(fname)[-2]
            # после даты у меня может быто место съёмки или название
            # события, по этому укорачиваем длинну названия.
            # файл лежит в папке назначения?
            if imdir == realdir[0:len(imdir)]:
            	print(os.path.split(fname)[-1] + "  ok")
            	continue
            elif not os.path.exists(imdir): 
                print("making dir %s"%imdir)
                os.mkdir(imdir)
            try:
            	nfname = os.path.join(imdir,  os.path.split(fname)[-1])
            	i = 0
            	# сравниваем и решаем что делать в функции
            	compare(i, fname, nfname, nfname)
            except OSError:
            	pritn("OSError")
            except WindowsError:
            	print("error with %s/n"%fname)
    if not recur:print(" sorting completed!")

##########
def del_empty_dirs(path):
	for d in os.listdir(path):
		a = os.path.join(path, d)
		if os.path.isdir(a):
			del_empty_dirs(a)
			if not os.listdir(a):
				os.rmdir(a)
				print(a, " deleted")
				
##########
def md5sum(name):
	
	md5 = hashlib.md5()
	with open(name, 'rb') as f:
		while True:
			buf = f.read(4096)
			if not buf:
				break
			md5.update(buf)
		return(md5.hexdigest())
    
##########
# a - что, b - с чем, c - basename
def compare(i, a, b, c):
	# файл есть?
	if os.path.isfile(b):
		# он или нет
		# файл лежит в папке назначения?
		if a != b:
		   if md5sum(a) == md5sum(b):
			   print("File %s exists, delete."%os.path.split(a)[-1])
			   try:
			   	os.remove(a)
			   	print("File %s exists, delete."%os.path.split(a)[-1])
			   except PermissionError:
			   	print("Permission denied: %s or %s" %(os.path.split(a)[-1], os.path.split(a)[-2]))
		   else:
			   # если есть файл с таким же названием сочиняем новое имя
			   i += 1
			   p = Path(c)
			   b = (Path(p.parent, "{}_{}".format(p.stem, i) + p.suffix))
			   print(os.path.split(a)[-1] + " rename " + os.path.split(b)[-1])
			   compare(i, a, b, c)
	else:
		# Копируем фотку в папку и удаляем оригинал
		shutil.copyfile(a,  b)
		print(os.path.split(b)[-1] + "  move")
		try:
		    os.remove(a)
		except PermissionError:
			print("Permission denied: %s or %s" %(os.path.split(a)[-1], os.path.split(a)[-2]))
		
##########
image_sort(dirname)
print(" delete empty folders")
del_empty_dirs(dirname)
print(" deleted completed!")