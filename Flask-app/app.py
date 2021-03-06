import os, json, shutil
from path import Path
from zipfile import ZipFile 
from flask import Flask, render_template, request, flash, send_from_directory, redirect, url_for
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = "6efdd6116ae6569e5d0fdca0be9a8644"
app.config['UPLOAD_PATH'] = 'uploads/'
project_dir = os.path.dirname(os.path.abspath(__file__))
#app.config['MAX_CONTENT_LENGTH'] = 4 * 1024 * 1024 # maximum file size = 4mb 

''' PWA Stuff '''
# only trigger SSLify if the app is running on Heroku
if 'DYNO' in os.environ: 
	from flask_sslify import SSLify
	sslify = SSLify(app)
	
@app.route('/sw.js', methods=['GET'])
def sw():
    return app.send_static_file('sw.js')

@app.route('/offline.html')
def offline():
	return app.send_static_file('offline.html')

''' Routes/views | Main Application Stuff ''' 

vidFiles = []

@app.route('/download')
def download():
	return send_from_directory(os.path.join(project_dir,app.config['UPLOAD_PATH']), filename='subtitles_renamed.zip', as_attachment=True, attachment_filename='subtitles_renamed.zip')

@app.route('/receiver', methods=['POST']) # AJAX receiver route
def get_data():
	data = request.get_json()
	global vidFiles
	vidFiles = data['data']
	return

@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
	if request.method == 'POST':
        # check if the post request has the file part
		if 'subFiles' not in request.files:
			flash('No file part', 'danger')
			return redirect(request.url)
		subFiles = []
		for f in request.files.getlist('subFiles'):
			filename = secure_filename(f.filename.split('/')[1])
			f.save(os.path.join(app.config['UPLOAD_PATH'], filename))
			subFiles.append(filename)
		sub_format = os.path.splitext(subFiles[0])[1]
		global vidFiles
		rename_files(vidFiles, subFiles, sub_format)
		return render_template('home2.html', subFiles=subFiles, vidFiles=vidFiles)
	try:
		os.mkdir(app.config['UPLOAD_PATH'])
	except FileExistsError:
		shutil.rmtree(app.config['UPLOAD_PATH'], ignore_errors=True)
		os.mkdir(app.config['UPLOAD_PATH'])
	return render_template('home.html')

def rename_files(vidFiles, subFiles, sub_format):
	vidFiles.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
	subFiles.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))
	with Path(os.path.join(project_dir, app.config['UPLOAD_PATH'])) as cwd:
		for i,vname in enumerate(vidFiles):
			os.rename(subFiles[i], os.path.splitext(vname)[0]+sub_format)
		files = os.listdir('.')
		with ZipFile('subtitles_renamed.zip','w') as zip:
			for file in files: 
				zip.write(file)
		for file in files:
			os.remove(file)
	return redirect(url_for('download'))

if __name__ == "__main__":
    app.run(debug=False)
