from flask import *
# from heatmap import *
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = os.path.expanduser('~') + '/Documents/flaskapp/static/submitted_files/'

app = Flask(__name__)
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/output', methods=['POST', 'GET'])
def output():
    if request.method == 'POST':
        urls = {
            "chord": [
                'http://iris.rnet.missouri.edu/coneva/jobs/2020-05-20-21-34-36/job_id_1/chord/top5.png',
                'http://iris.rnet.missouri.edu/coneva/jobs/2020-05-20-21-34-36/job_id_1/chord/topL10.png'
            ],
            "distmap": [
                'http://deep.cs.umsl.edu/prayogrealdistance/jobs/T1024/T1024.realdist.npy.png',
                'http://deep.cs.umsl.edu/prayogrealdistance/jobs/T1025/T1025.realdist.npy.png'
            ]
        }
        data = {
            'urls': urls
        }
        rr_path = ''
        pdb_path = ''
        if 'rr-file' not in request.files:
            flash('No file part')
            return redirect('/')
        else:
            rrfile = request.files['rr-file']
            if rrfile.filename == '':
                flash('No selected file')
                return redirect('/')
            name_rr =  rrfile.filename
            rr_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(name_rr))
            rrfile.save(rr_path)
            
            print('rr file :', rrfile.filename)
        if 'pdb-file' not in request.files:
            flash('No file found')
            return redirect('/')
        else:
            pdbfile = request.files['pdb-file']
            if pdbfile.filename == '':
                flash('No selected file')
                return redirect('/')
            name_pdb =  pdbfile.filename
            pdb_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(name_pdb))
            pdbfile.save(pdb_path)

        if(name_rr != '' and name_pdb != ''):
            img_name = name_rr.split('.')[0] + '_heatmap.png'
            os.system('python3 heatmap.py ' + rr_path + ' ' + pdb_path + ' ' + img_name)
            # res = plot_dl_vs_3dmodel(rr_path, pdb_path)
            res = {
                'rr_name': name_rr,
                'pdb_name': name_pdb,
                'path': f'static/images/{img_name}'
            }
            data['res'] = res

        return render_template('output.html', data=data)
    else:
        return render_template('output.html')

if __name__ == '__main__':
    app.run(debug=True)