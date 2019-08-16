from flask import redirect, render_template, request, Blueprint, send_file, session, url_for
from flask_iiif.api import IIIFImageAPIWrapper,MultimediaImage
from urllib import urlretrieve
from PIL import Image
import os

from models import Tag, tag_identifier, Pic, Tag_Hierarchy, search
from testiiif import db, get_exifs,setup, basedir, redirect_url

from forms import CropForm, BatchUpdateForm, AddTag2PicForm, MoveFolderForm, SearchForm, AddFolderForm, UpdateMetadataForm, AddTagForm

core = Blueprint('core', __name__)

@core.route('/',methods=["GET", "POST"])
def index():
        return redirect(url_for('core.home', folder='.root'))

@core.route('/view/<folder>', methods=["GET", "POST"])
def home(folder):
	print "hi"
	folderForm = AddFolderForm()
	picForm = UpdateMetadataForm()
	searchForm = SearchForm()
	tagForm = AddTagForm()
	addTagForm = AddTag2PicForm()
	moveForm = MoveFolderForm()
	batchForm = BatchUpdateForm()

 	currentFolder = Tag.query.filter((Tag.name==folder) & (Tag.isFolder==True)).first_or_404()
	folder_hierarchy = Tag_Hierarchy.query.filter_by(node_id = currentFolder.id).order_by(Tag_Hierarchy.depth.desc()).all()
	folder_path = [Tag.query.filter_by(id = h.parent_id).first() for h in folder_hierarchy]
	
	moveForm.all_folders.data = currentFolder

	if folderForm.submitFolder.data and folderForm.validate_on_submit():
		name = folderForm.name.data
		new_folder = Tag(name, isFolder=True)
		currentFolder.hierarchy(new_folder.id)
		
		return redirect(url_for('core.home', folder=folder))
	if tagForm.submitTag.data and tagForm.validate_on_submit():
		name = tagForm.name.data
		new_tag = Tag(name)

	tag_list = Tag.query.filter_by(isFolder=False).all()
	children = currentFolder.get_direct_children()
	pics = Pic.query.filter(Pic.tags.any(id=currentFolder.id)).all()
	
	return render_template('home.html', batchForm=batchForm, moveForm=moveForm, addTagForm=addTagForm, tagForm=tagForm, searchForm=searchForm, picForm=picForm, folderForm=folderForm, tag_list=tag_list, folder_path=folder_path, pics=pics, folders=children)

@core.route('/view/<folder>/delete_folder/<delete_id>', methods=["GET", "POST"])
def delete_folder(folder, delete_id):
	tbd = Tag.query.filter_by(id=delete_id).first_or_404()
	

@core.route('/search', methods=["GET", "POST"])
def search_for():
        folderForm = AddFolderForm()
        picForm = UpdateMetadataForm()
        searchForm = SearchForm(request.form)
        tagForm = AddTagForm()
        addTagForm = AddTag2PicForm()
        moveForm = MoveFolderForm()
        batchForm = BatchUpdateForm()

	tag_list = Tag.query.filter_by(isFolder=False).all()
	children = []
        pics = []#Pic.query.filter(Pic.tags.any(id=currentFolder.id)).all()
	
	if request.method == "POST" and searchForm.submitSearch.data:# and searchForm.validate():
                print "heeey"
                data = {}
                tb = searchForm.meta.model.__tablename__
		tb_tags = Tag.__table__.name
		
		tag_lst = []
                for field in searchForm:
		        if field != searchForm.submitSearch and field.data and field.data != "None":
				if field != searchForm.tags and field != searchForm.folder:
					data[tb+'.'+ field.name] = field.data
				else:
					tag_lst.append(str(field.data.id))
		data[tb_tags + '.id'] = tag_lst

               	print data
		if data:
			pics = search(data)
			print pics
                else:
			pics = {}
		return render_template('home.html', moveForm=moveForm, batchForm=batchForm, addTagForm=addTagForm, searchForm=searchForm, picForm=picForm, tagForm=tagForm, folderForm=folderForm, tag_list=tag_list, pics=pics, folders=[])
	'''
        print "searchForm"
        print searchForm.submitSearch.data
        print searchForm.validate()
        '''


        return render_template('home.html', moveForm=moveForm, batchForm=batchForm, searchForm=searchForm, addTagForm=addTagForm, tagForm=tagForm, picForm=picForm, folderForm=folderForm, pics=pics, folders=children)


@core.route('/view/photo/<photo>', methods=["GET", "POST"])
def single(photo):
	pic = Pic.query.filter_by(id=photo).first_or_404()
	picForm = UpdateMetadataForm(request.form, obj=pic)
	addTagForm = AddTag2PicForm()
	moveForm = MoveFolderForm()

	for t in pic.tags:
		if t.isFolder:
			print t
			moveForm.all_folders.data = t
			break

	if request.method=="POST" and picForm.submitMetadata.data:
		for field in picForm:
                        if not field.data:
				field.data = None
		picForm.populate_obj(pic)
		db.session.add(pic)
		db.session.commit()
		return redirect(redirect_url())
	print "hey"
	return render_template('photo_view.html', moveForm=moveForm, addTagForm=addTagForm, picForm=picForm, basedir=basedir, pic = pic)

@core.route('/view/photo/<photo>/addTag', methods=["GET", "POST"])
def addingTag(photo):
        pic = Pic.query.filter_by(id=photo).first_or_404()
        addTagForm = AddTag2PicForm(request.form)

        if request.method=="POST" and addTagForm.addTag.data:
                pic.add_tag(addTagForm.all_tags.data)
        return redirect(url_for('core.single', photo=photo))

@core.route('/view/photo/<photo>/move', methods=["GET", "POST"])
def movingFolder(photo):
        pic = Pic.query.filter_by(id=photo).first_or_404()
        moveForm = MoveFolderForm(request.form)

        if request.method=="POST" and moveForm.changeFolder.data:
		pics = []
                for id in filter(None, moveForm.ids.data.split(",")):
	                pics.append(Pic.query.filter_by(id=int(id)).first())

		for pic in pics:
			pic.add_tag(moveForm.all_folders.data)

        print "tagsdgaseg"
	return redirect(redirect_url())
        #return redirect(url_for('core.single', photo=photo))



@core.route('/view/photo/<photo>/deleteTag/<tag>',methods=["GET", "POST"])
def remove_tag(photo, tag):
	pic = Pic.query.filter_by(id=photo).first_or_404()
	t = Tag.query.filter_by(id=tag).first_or_404()
	pic.remove_tag(t)
	print "removed tag"
	return redirect(url_for('core.single', photo=photo))

@core.route('/test', methods=["GET", "POST"])
def iiif():
	form = UpdateMetadataForm()
        return render_template('hi.html', form=form)
	#image = IIIFImageAPIWrapper.from_file(basedir+'/statmnt/IMG_9761.JPG')
        image = IIIFImageAPIWrapper.from_file(basedir+'/mnt/rdf/jcm10/crc_summer_dev/photo_dump_1/IMG_9763.JPG')
        #image = IIIFImageAPIWrapper.from_file(basedir+'/mnt/rdf/jcm10/crc_summer_dev/miller_wright/HRC_Image_Archiving_Interface/AESP-IT-7.pdf')

        # Rotate the image
        image.rotate(90)

        # Resize the image
        image.resize('300,200')

        # Crop the image
        image.crop('20,20,400,300')

        # Make the image black and white
        image.quality('grey')

        # Finaly save it to /tm
        image.save(basedir + '/static/test_pdf.jpg')

        return send_file(image.serve(), mimetype='image/jpeg')


@core.route('/populatedb', methods=["GET", "POST"])
def popdb():
	path = basedir + '/mnt/rdf/jcm10/crc_summer_dev/hi/'
	dirs = os.listdir( path )

	for f in dirs:
		if f[0] != '.':
			exif = get_exifs([path+f])[path+f]
			date = exif['DateTime']
			pic = Pic(path+str(f), date=date)
			db.session.add(pic)
	'''
        path =basedir+'/mnt/rdf/jcm10/crc_summer_dev/photo_dump_1/IMG_9763.JPG'
        exif = get_exifs([path])[path]
        date = exif['DateTime']
        pic = Pic(path, 'test1', date=date)
        ''' 
	
	tag1 = Tag("folder1", isFolder=True)
	tag6 = Tag("folder2", isFolder=True)
        tag2 = Tag("pictag")
        tag3 = Tag("subfolder1", isFolder=True)
        tag5 = Tag("subsubfolder", isFolder=True)
        tag4 = Tag("subfolder2", isFolder=True)
        #print "hi"

        tag1.hierarchy(tag3.id)
        tag1.hierarchy(tag4.id)
        tag3.hierarchy(tag5.id)

        #db.session.add(Tag_Hierarchy(tag1.id, tag1.id, 0))
        #db.session.commit()

        db.session.commit()

        pic.add_tag(tag2)
        pic.add_tag(tag1)

        #return redirect(url_for('core.printdb'))
        return '<h1>' + str(exif) + '</h1>'

@core.route('/testdb', methods=["GET", "POST"])
def testdb():
        #pic = Pic.query.all()[0]
        #tag = Tag.query.filter_by(name='pictag').first()
        #print tag
        #print pic
        #pic.remove_tag(tag)
        #return redirect(url_for('core.printdb'))
	return '<h1>' + str(search({'pics.title': 'test', 'pics.id':11})) + '</h1>'
        '''
        tb = pic.get_thumbnail(200,200)
        if tb == -1:
                return "nope"
        image = IIIFImageAPIWrapper.from_file(tb.path)
        return send_file(image.serve(), mimetype='image/jpeg')
        #return str(Tag_Hierarchy.query.filter_by(depth=0).all())
        '''

@core.route('/cleardb', methods=["GET", "POST"])
def cleardb():
        meta = db.metadata
        for table in reversed(meta.sorted_tables):
                print 'Clear table %s' % table
                db.session.execute(table.delete())
        db.session.commit()
	setup()
        return redirect(url_for('core.printdb'))

@core.route('/rotate/<photo>/<dir>')
def rotate(photo, dir):
	pic = Pic.query.filter_by(id=photo).first_or_404()
	rotate = int(pic.rotation[1:])
	if dir == 'l':
		rotate -= 90
		while rotate < 0:
			rotate += 360
	elif dir == 'r':
		rotate += 90
		while rotate >= 360:
			rotate -= 360
	pic.rotation = pic.rotation[0] + str(rotate)
	db.session.commit()
	return redirect(redirect_url())

@core.route('/view/crop/<photo>', methods=["GET","POST"])
def crop(photo):
	pic = Pic.query.filter_by(id=photo).first_or_404()
	cropForm = CropForm(request.form)

	if request.method=="POST" and cropForm.submitCoor.data:
		pic.region = cropForm.coor.data
		db.session.commit()
		return redirect(url_for('core.single',photo=photo))
	
	return render_template('crop_view.html', cropForm=cropForm, pic = pic)

@core.route('/temp')
def temp():
	print type(Pic.query.first())
	result = db.session.execute('select distinct pics.name as pname, tags.name as tname from pics inner join tag_identifier as ti on pics.id=ti.pic_id inner join tags on tags.id=ti.tag_id where tags.name in ("pictag", "folder1") group by ;');	
	tid = Tag.query.filter_by(name='pictag').first().id
	folder = Tag.query.filter_by(name='folder1').first().id
	where = '(tags.id in ('+ str(tid) + ',' + str(folder) + ')'
	pics = Pic.query.join(Tag, Pic.tags).filter(db.text(where)).group_by(Pic.name).having(func.count(Pic.name) == 2).all()
	#pics = Pic.query.filter(Pic.tags.any(Tag.id==tid)).all()
	print pics
	tmp = {}
	print result.fetchall()
	print type(result.fetchall())
	for r in result:
		tmp[r[0]] = dict(r.items())
	return tmp

@core.route('/printdb', methods=['GET','POST'])
def printdb():
        return str(Pic.query.all()) + "<br><br> tags:" + str(Tag.query.all()) + "<br><br> hierarchy:" + str(Tag_Hierarchy.query.all())
