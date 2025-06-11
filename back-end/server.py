from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import subprocess
import pandas as pd
from min import process_literature
import time
import shutil

# 路径统一
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LITERATURE_FOLDER = os.path.join(BASE_DIR, 'literature')
RESULT_FILE = os.path.join(BASE_DIR, 'results', 'literature_summary.xlsx')

app = Flask(
    __name__,
    static_folder='../front-end',      # 指定静态文件目录
    static_url_path=''                 # 让 /style.css 直接映射到静态目录
)

@app.route('/')
def serve_index():
    return send_from_directory(os.path.join(BASE_DIR, '../front-end'), 'index.html')

@app.route('/your-backend-api', methods=['POST'])
def your_backend_api():
    api_key = request.form.get('api_key')
    # 这里可以添加你需要的处理逻辑
    return jsonify({'message': 'API key received', 'api_key': api_key})

@app.route('/upload', methods=['POST'])
def upload_file():
    # 支持多文件上传
    if 'files' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    files = request.files.getlist('files')
    if not files or all(f.filename == '' for f in files):
        return jsonify({'error': 'No selected file'}), 400
    # 确保 literature 文件夹存在
    if not os.path.exists(LITERATURE_FOLDER):
        os.makedirs(LITERATURE_FOLDER)
    saved_filenames = []
    for file in files:
        if file and file.filename:
            save_path = os.path.join(LITERATURE_FOLDER, file.filename)
            file.save(save_path)
            saved_filenames.append(file.filename)
    return jsonify({'message': 'Files uploaded successfully', 'filenames': saved_filenames})

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

@app.route('/generate_excel', methods=['POST'])
def generate_excel():
    data = request.json
    headers = data.get('headers', [])
    api_key = data.get('api_key', None)
    if not headers or not isinstance(headers, list):
        return jsonify({'error': 'Invalid headers'}), 400
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400

    rows = []
    for filename in os.listdir(LITERATURE_FOLDER):
        if filename.endswith('.pdf'):
            file_path = os.path.join(LITERATURE_FOLDER, filename)
            try:
                row = process_literature(file_path, api_key, headers)
                rows.append(row)
            except Exception as e:
                error_row = [f"{filename} 处理失败: {str(e)}"] + [""] * (len(headers) - 1)
                rows.append(error_row)
            time.sleep(60)  # 每处理一个文件等待30秒

    df = pd.DataFrame(rows, columns=headers)
    result_dir = os.path.dirname(RESULT_FILE)
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    df.to_excel(RESULT_FILE, index=False)
    return jsonify({'message': 'Excel file generated', 'headers': headers})

@app.route('/clear_folders', methods=['POST'])
def clear_folders():
    for folder in ['literature', 'results']:
        folder_path = os.path.join(os.getcwd(), folder)
        if os.path.exists(folder_path):
            for filename in os.listdir(folder_path):
                file_path = os.path.join(folder_path, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception:
                    pass
    return '', 204

if __name__ == '__main__':
    if not os.path.exists(LITERATURE_FOLDER):
        os.makedirs(LITERATURE_FOLDER)
    app.run(host='0.0.0.0', port=5002, debug=True)
