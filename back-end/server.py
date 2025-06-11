from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import subprocess
import pandas as pd

# 路径统一
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LITERATURE_FOLDER = os.path.join(BASE_DIR, 'literature')
RESULT_FILE = os.path.join(BASE_DIR, 'results', 'literature_summary.xlsx')

app = Flask(__name__)

@app.route('/')
def serve_index():
    return send_from_directory(os.path.join(BASE_DIR, '../front-end'), 'index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    # 确保 literature 文件夹存在
    if not os.path.exists(LITERATURE_FOLDER):
        os.makedirs(LITERATURE_FOLDER)
    save_path = os.path.join(LITERATURE_FOLDER, file.filename)
    file.save(save_path)
    return jsonify({'message': 'File uploaded successfully', 'filename': file.filename})

@app.route('/run', methods=['POST'])
def run_multi():
    try:
        result = subprocess.run(
            ['/usr/bin/python3', os.path.join(BASE_DIR, 'multi.py')],
            check=True, capture_output=True, text=True
        )
        return jsonify({'message': 'multi.py executed successfully', 'stdout': result.stdout, 'stderr': result.stderr})
    except subprocess.CalledProcessError as e:
        return jsonify({'error': str(e), 'stdout': e.stdout, 'stderr': e.stderr}), 500

@app.route('/result', methods=['GET'])
def get_result():
    if not os.path.exists(RESULT_FILE):
        return jsonify({'error': 'Result file not found'}), 404
    df = pd.read_excel(RESULT_FILE)
    return df.to_json(orient='records', force_ascii=False)

@app.route('/download', methods=['GET'])
def download_result():
    if not os.path.exists(RESULT_FILE):
        return jsonify({'error': 'Result file not found'}), 404
    return send_file(RESULT_FILE, as_attachment=True)

if __name__ == '__main__':
    if not os.path.exists(LITERATURE_FOLDER):
        os.makedirs(LITERATURE_FOLDER)
    app.run(host='0.0.0.0', port=5002, debug=True)
