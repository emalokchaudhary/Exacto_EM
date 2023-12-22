from flask import Flask, jsonify, request
import os
import shutil
import signal
from pdfFilesNew import processDocument

from flask.ext.cors import CORS, cross_origin

app = Flask(__name__)
cors = CORS(app, resources={r"/foo": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'

child_pid = -1


@app.route('/api/v0/cognitive_services/thomson/', methods=['POST'])
@cross_origin(origin='*', headers=['Content-Type', 'Authorization'])
def get_ocr_result():
    global child_pid

    if 'file' not in request.files:
        return jsonify({'error': "No File found"})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': "File Name Error"})

    image_name = file.filename
    output_path = os.path.abspath("data/inputs")

    if os.path.isdir(output_path):
        shutil.rmtree(output_path)
    os.makedirs(output_path)
    file.save(os.path.join(output_path, image_name))

    inputPath = os.path.abspath('data/inputs')
    outputPath = os.path.abspath('data/outputs')
    xmlDir = os.path.abspath('data/XML')

    dict = processDocument(inputPath, outputPath, xmlDir)
    # if child_pid != -1:
    # 	os.kill(child_pid, signal.SIGTERM)
    #
    # try:
    # 	child_pid = os.fork()
    # except OSError:
    # 	exit("Could not create a child process")
    #
    # if child_pid == 0:
    # 	os.system("/home/sg/envs/python27/bin/python exacto_ls.py")
    # 	os._exit(0)

    return jsonify(dict)


if __name__ == '__main__':
    app.debug = False
    app.run(host='0.0.0.0', port=9000)