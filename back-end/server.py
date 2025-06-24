from flask import Flask, request, jsonify, send_file, send_from_directory
import os
import subprocess
import pandas as pd
from prompt import process_literature
from APIconnection import test_moonshot_connection, test_openai_connection
import time
import shutil
import requests
import httpx

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

@app.route('/your-backend-apihost', methods=['POST'])
def your_backend_host():
    api_host = request.form.get('api_host')
    # 这里可以添加你需要的处理逻辑
    return jsonify({'message': 'API host received', 'api_host': api_host})


@app.route('/test_connection', methods=['POST'])
def test_connection():
    data = request.json
    api_type = data.get('api_type', 'moonshot')  # 默认为moonshot
    api_host = data.get('api_host')
    api_key = data.get('api_key')
    
    if not api_key:
        return jsonify({
            "success": False,
            "message": "API key is required"
        }), 400

    if api_type == 'Moonshot':
        if not api_host:
            return jsonify({
                "success": False,
                "message": "Moonshot API host is required"
            }), 400
        success, message = test_moonshot_connection(api_host, api_key)
    elif api_type == 'OpenAI':
        success, message = test_openai_connection(api_host,api_key)
    else:
        return jsonify({
            "success": False,
            "message": "Unsupported API type"
        }), 400

    return jsonify({
        "success": success,
        "message": message
    })


@app.route('/upload', methods=['POST'])
def upload_files():
    if not request.files:
        print('No files in request')  # 调试输出
        return {'error': 'No file part'}, 400

    saved_files = []
    for key in request.files:
        file = request.files[key]
        if file.filename == '':
            print(f'No selected file for key {key}')  # 调试输出
            continue

        # Save file to the literature folder
        file_path = os.path.join(LITERATURE_FOLDER, file.filename)
        file.save(file_path)
        saved_files.append(file.filename)
        print(f'File saved to {file_path}')  # 调试输出

    if not saved_files:
        return {'error': 'No files were uploaded'}, 400

    return {'message': 'Files uploaded successfully', 'files': saved_files}, 200  




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
    api_type = data.get('api_type', 'moonshot') 
    api_key = data.get('api_key', None)
    api_host = data.get('api_host', None)
    if not headers or not isinstance(headers, list):
        return jsonify({'error': 'Invalid headers'}), 400
    if not api_key:
        return jsonify({'error': 'API key is required'}), 400
    if not api_host:
        return jsonify({'error': 'API host is required'}), 400

    rows = []
    for filename in os.listdir(LITERATURE_FOLDER):
        if filename.endswith('.pdf'):
            file_path = os.path.join(LITERATURE_FOLDER, filename)
            try:
                row = process_literature(file_path, api_type, api_host, api_key, headers)
                row.insert(0, filename)
                rows.append(row)
            except Exception as e:
                error_row = [filename] + [f"处理失败: {str(e)}"] + [""] * (len(headers) - 1)
                rows.append(error_row)
            time.sleep(60)  # 每处理一个文件等待30秒

    df = pd.DataFrame(rows, columns=['文件名'] + headers)
    result_dir = os.path.dirname(RESULT_FILE)
    if not os.path.exists(result_dir):
        os.makedirs(result_dir)
    #当
    df.to_excel(RESULT_FILE, index=False)
    return jsonify({'message': 'Excel file generated', 'headers': ['文件名'] + headers})



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


@app.route('/delete', methods=['POST'])
def delete_file():
    data = request.get_json()
    filename = data.get('filename')

    if not filename:
        return {'error': 'Filename not provided'}, 400

    file_path = os.path.join(LITERATURE_FOLDER, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        print(f'File {filename} deleted from {LITERATURE_FOLDER}')  # 调试输出
        return {'message': f'File {filename} deleted successfully'}, 200
    else:
        print(f'File {filename} not found in {LITERATURE_FOLDER}')  # 调试输出
        return {'error': f'File {filename} not found'}, 404

if __name__ == '__main__':
    if not os.path.exists(LITERATURE_FOLDER):
        os.makedirs(LITERATURE_FOLDER)
    app.run(host='0.0.0.0', port=5002, debug=True)
