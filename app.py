from flask import *

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/output')
def output():
    urls = {
        "chord": [
            'http://iris.rnet.missouri.edu/coneva/jobs/2020-05-20-21-34-36/job_id_1/chord/top5.png',
            'http://iris.rnet.missouri.edu/coneva/jobs/2020-05-20-21-34-36/job_id_1/chord/topL10.png'
        ],
        "distmap": [
            'http://deep.cs.umsl.edu/prayogrealdistance/jobs/T1024/T1024.realdist.npy.png',
            'http://deep.cs.umsl.edu/prayogrealdistance/jobs/T1025/T1025.realdist.npy.png',
            'http://deep.cs.umsl.edu/prayogrealdistance/jobs/T1026/T1026.realdist.npy.png',
            'http://deep.cs.umsl.edu/prayogrealdistance/jobs/T1027/T1027.realdist.npy.png',
            'http://deep.cs.umsl.edu/prayogrealdistance/jobs/T1028/T1028.realdist.npy.png'
        ]
    }
    return render_template('output.html', urls=urls)

if __name__ == '__main__':
    app.run(debug=True)