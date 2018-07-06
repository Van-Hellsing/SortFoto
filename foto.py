#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# sorts images by date
 
import os,sys
from PIL import Image
import piexif
import shutil 

# задаём директорию для сортировки
rootdir = os.getcwd()
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
            	print("seems not image: %s"%fname)
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
            	
            foldername = datetime[5:7] + "." + datetime[0:4]
            # папка назначения
            imdir = os.path.join(rootdir, foldername)
            # файл лежит в папке назначения?
            if imdir == os.path.split(fname)[-2]:
                continue
            elif not os.path.exists(imdir): 
                print("making dir %s"%imdir)
                os.mkdir(imdir)
            try:
            	# Копируем фотку в папку и удаляем оригинал
                shutil.copyfile(fname,  os.path.join(imdir,  os.path.split(fname)[-1]))
                os.remove(fname)
            except WindowsError:
                print("error with %s/n"%fname)
    if not recur:print("  sorting completed!")

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

image_sort(dirname)
print("   delete empty folders")
del_empty_dirs(dirname)
print("  deleted completed!")
