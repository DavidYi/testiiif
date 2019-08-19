from watchdog.observers.polling import PollingObserver
from watchdog.events import RegexMatchingEventHandler, FileSystemEventHandler
import time
import os
from shutil import copyfile
from models import Pic,Tag, db
from testiiif import get_exifs
from PIL import Image
import sys
import fitz


def run_watcher():
	watcher = Watcher()
	watcher.run()

DIRECTORY_TO_WATCH = "/var/www/testiiif/mnt/rdf/jcm10/crc_summer_dev/hi"


def split(pdf_filepath,jpg_dir):
	doc = fitz.open(pdf_filepath)

	#borrowed from https://stackoverflow.com/questions/2693820/extract-images-from-pdf-without-resampling-in-python?lq=1
	for i in range(len(doc)):
		print i
		for img in doc.getPageImageList(i):
			xref = img[0]
			pix = fitz.Pixmap(doc, xref)
			output_filename = "%s-%s.jpg" % (i, xref)
			output_filepath = os.path.join(jpg_dir,output_filename)
			print output_filepath
			
			pix = fitz.Pixmap(fitz.csRGB, pix)
			img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
			img.save(output_filepath,"JPEG")
	
			pix = None



class Watcher:

	def __init__(self):
		self.observer = PollingObserver()

	def run(self):
		print "starting watch woof woof!!!!!!"

		event_handler = Handler()       
		self.observer.schedule(event_handler, DIRECTORY_TO_WATCH, recursive=True)
		self.observer.start()

		try:
			while True:
				time.sleep(5)
		except:
			self.observer.stop()
			print "Error"

		self.observer.join()


class Handler(RegexMatchingEventHandler):

	def __init__(self):
		super(Handler, self).__init__(ignore_regexes=["^\..*", ".*/\..*"])


        def on_created(self, event):
		path = os.path.normpath(event.src_path)
		print "************create new file at " + str(path)
	
		if event.is_directory:
			return

		filename = str(os.path.basename(path))
                filepath = str(os.path.dirname(path))
                print filename
                print filepath

		tmp = filepath.replace(DIRECTORY_TO_WATCH, '')
		#base = os.path.join(DIRECTORY_TO_WATCH, '../inputs/')
		#filepath = filepath.replace(DIRECTORY_TO_WATCH, base, 1)

		name = os.path.splitext(filename)


		if name[1].lower() == '.pdf':

			jpg_dir = os.path.join(filepath,name[0])
			print jpg_dir
			if os.path.exists(jpg_dir):
				return
			os.makedirs(jpg_dir)
			
			try:
				split(path,jpg_dir)
			except:
				print("Failed on", path + ".pdf")
				print("Unexpected error:", sys.exc_info()[0])
				print sys.exc_info()
			return
		#if os.path.splitext(os.path.basename(path))[0][0] == '.':
		#	return 
		

		direct = tmp.split(os.sep)
		addition = direct[0]

		filepath =  os.path.normpath(filepath)
		
		print filepath
		print "yoooo"
		print tmp
		print direct
		parent = ''
		direct = list(filter(None, direct))
		
		for folder in direct:
			if not folder:
				continue
			f_tag = Tag.query.filter_by(name=str(folder)).first()
			if not f_tag:
				print "creating tag for" + str(folder)
				f_tag = Tag(str(folder), isFolder=True)
				if folder != direct[0]:
					parent.hierarchy(f_tag.id)
					db.session.commit()
					print 'creating heirarchy to ' + str(parent)
			parent = f_tag
			addition = os.path.join(addition, folder)
		
		#if not os.path.exists(filepath):
		#	os.makedirs(filepath)
				
		new_path = os.path.join(filepath, filename)
		if Pic.query.filter_by(path=new_path).first():
			return
		#copyfile(path,new_path)
		
		try:
			exif = get_exifs([new_path])[new_path]
        		date = exif['DateTime']
			new_pic = Pic(str(new_path), date=date)
                except:
			new_pic = Pic(str(new_path))
		db.session.add(new_pic)
                db.session.commit()
		if len(direct) > 0:
			new_pic.add_tag(f_tag)
			db.session.commit()		


        def on_deleted(self, event):
		if event.is_directory:
			return
		if os.path.splitext(os.path.basename(event.src_path))[0][0] == '.':
                        return 
                print "************deleted" + str(event.src_path)
                print os.stat(event.src_path)
		
		pic_deleted = Pic.query.filter_by(path=event.src_path).first()
                db.session.delete(pic_deleted)
                db.session.commit()
		

#print os.stat('/var/www/testiiif/mnt/rdf/jcm10/crc_summer_dev/hi')
#run_watcher()
