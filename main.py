import os
from flask import Flask, request, jsonify, send_from_directory
import pandas as pd
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = str(uuid.uuid4()) + '.csv'
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return jsonify({'message': 'File uploaded successfully'}), 201

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/files', methods=['GET'])
def list_files():
    files = os.listdir(UPLOAD_FOLDER)
    file_info = []
    for filename in files:
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        if os.path.isfile(file_path) and allowed_file(filename):
            data = pd.read_csv(file_path)
            columns = data.columns.tolist()
            file_info.append({'filename': filename, 'columns': columns})
    
    return jsonify({'files': file_info})

@app.route('/data/<filename>', methods=['GET'])
def get_data(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    data = pd.read_csv(file_path)

    query_params = request.args.to_dict()
    if 'filter_column' in query_params and 'filter_value' in query_params:
        filter_column = query_params['filter_column']
        filter_value = query_params['filter_value']
        data = data[data[filter_column] == filter_value]

    if 'sort_column' in query_params:
        sort_column = query_params['sort_column']
        ascending = True
        if 'sort_direction' in query_params and query_params['sort_direction'].lower() == 'desc':
            ascending = False
        data = data.sort_values(by=sort_column, ascending=ascending)

    return data.to_json(orient='records'), 200

@app.route('/files/<filename>', methods=['DELETE'])
def delete_file(filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    
    if not os.path.exists(file_path):
        return jsonify({'error': 'File not found'}), 404
    
    os.remove(file_path)
    return jsonify({'message': 'File deleted successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
