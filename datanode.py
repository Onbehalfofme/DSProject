import json
import math
import os
from random import randint
import shutil

import requests
from flask import Flask, request, Response
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
file_names = {}
files = []
free_index = 0
namenode = ''
base_path ='/dfs'


def create_dir(path):
    paths = path.split('/')
    current_path = '/'
    for p in paths[:-1]:
        current_path += p
        if not os.path.exists(current_path):
            os.mkdir(current_path)


@app.route('/upload', methods=['POST'])
def download_file():
    path = base_path+request.headers.get('File-Name', type=str)
    path1= base_path+request.headers.get('File-Name', type=str)
    file_id = request.headers.get('File-Id', type=int)
    chunk_id = request.headers.get('Chunk-Id', type=int)
    chunk_length = request.headers.get('Chunk-Number', type=int)
    if file_names.get(file_id) is None:
        file_names.update({file_id: (len(files), path)})
        current_index = len(files)
        files.append([None for _ in range(chunk_length)])
    else:
        current_index = file_names.get(file_id)[0]

    files[current_index][chunk_id] = request.data

    if None not in files[current_index]:
        replications = request.headers.get('Replications', type=int)
        address = None
        if replications:
            replications += 1
        else:
            replications = 2
        if replications < 4:
            r = requests.get('http://' + namenode + '/replicate', headers={'path': path1})
            address = r.headers.get('address')
        file = bytearray()
        index = 0
        for chunk in files[current_index]:
            file.extend(bytearray(chunk))
            if address:
                headers = dict(request.headers)
                headers.update({'Replications': str(replications), 'Chunk-Id': str(index)})
                requests.post('http://' + address + '/upload', headers=headers, data=chunk)
                if index > len(files[current_index]):
                    index = 0
                else:
                    index += 1
        create_dir(path)
        with open(path, 'wb') as fp:
            fp.write(file)
        del files[current_index]
        del file_names[file_id]
        for d in file_names:
            if d[0] > current_index:
                file_names.update({d[0], (d[1][0] - 1, d[1][1])})

    return Response(status=200)


@app.route('/create', methods=['GET'])
def create_file():
    path = base_path+request.headers.get('File-Name', type=str)
    path1 = request.headers.get('File-Name', type=str)
    create_dir(path)
    replications = request.headers.get('Replications', type=int)
    address = None
    if replications:
        replications += 1
    else:
        replications = 2
    if replications <= 4:
        r = requests.get('http://' + namenode + '/replicate', headers={'path': path1})
        address = r.headers.get('address')
    open(path, 'a').close()
    if address:
        headers = dict(request.headers)
        headers.update({'Replications': str(replications)})
        requests.get('http://' + address + '/create', headers=headers)
    return Response(200)


@app.route('/download', methods=['GET'])
def upload_file():
    path = base_path+request.headers.get('File-Name', type=str)
    with open(path, 'rb') as fp:
        data = fp.read()
    return Response(status=200, response=data)


@app.route('/health', methods=['GET'])
def health():
    global namenode
    namenode = request.remote_addr
    f = requests.request('GET', 'https://ident.me')
    ip = f.text
    return Response(status=200, headers={'ip': str(ip)})


@app.route('/delete', methods=['GET'])
def delete():
    path = base_path+request.headers.get('path')
    os.remove(path)
    return Response(status=200)


@app.route('/rmdir')
def rmdir():
    path = request.headers.get('path')
    os.system('rm -rf ' + base_path+path)
    return Response(status=200)


@app.route('/info', methods=['GET'])
def file_info():
    path = base_path+request.headers.get('path')
    st = os.stat(path)
    data = {'size': str(st.st_size), 'last_accessed': str(st.st_atime), 'last_modified': str(st.st_mtime)}
    return Response(status=200, response=json.dumps(data))


@app.route('/copy', methods=['GET'])
def copy():
    old_path = base_path+request.headers.get('File-Name-Old')
    new_path = base_path+request.headers.get('File-Name-New')
    create_dir(new_path)
    os.system('sudo cp ' + old_path + ' ' + new_path)
    return Response(200)


@app.route('/init', methods=['get'])
def init():
    os.system('sudo rm -rf '+base_path)
    total, used, free = shutil.disk_usage('/')
    return Response(status=200, response=str(free).encode())


@app.route('/replicate', methods=['GET'])
def replicate():
    path = base_path+request.headers.get('path')
    address = request.headers.get('address')
    with open(base_path+path, 'rb') as fp:
        chunk = fp.read(1024)
        chunk_id = 0
        file_id = randint(0, 1000)
        chunk_number = math.ceil(os.path.getsize(path) / 1024)
        while chunk:
            requests.post('http://' + address + '/upload', data=chunk,
                          headers={'File-Name': path, 'File-Id': file_id, 'Chunk-Id': chunk_id,
                                   'Chunk-Number': chunk_number, 'Replications': 3})
            chunk_id += 1
    return Response(200)


@app.route('/move', methods=['GET'])
def move():
    old_path = base_path+request.headers.get('File-Name-Old')
    new_path = base_path+request.headers.get('File-Name-New')
    create_dir(new_path)
    os.system('sudo mv ' + old_path + ' ' + new_path)
    return Response(200)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
