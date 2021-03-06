from flask import Flask, Response, request
import requests
import random
from apscheduler.schedulers.background import BackgroundScheduler
from file_tree import FileTree
from flask_cors import CORS
import json
app = Flask(__name__)
CORS(app)

datanodes = ['3.136.157.131:5000', '18.191.130.115:5000', '3.14.73.21:5000']
deadnodes = []
file_tree = FileTree()


@app.route('/')
def hello_world():
    return str(datanodes) +'\n' + str(deadnodes)


def find_datanodes():
    subnet = '10.0.1.'
    for i in range(256):
        ip = subnet + str(i) + ":5000"
        try:
            response = requests.get("http://" + ip + "/health", timeout=10)
            node = response.headers.get('ip') + ":5000"
        except requests.exceptions.RequestException:
            continue
        if not node in datanodes:
            datanodes.append(node)
            print(ip + " success")

def heartbeat():
    for node in datanodes:
        try:
            requests.get("http://" + node + "/health", timeout=10)
            if node in deadnodes:
                synchronize(node)
                deadnodes.remove(node)
        except requests.exceptions.RequestException:
            if not node in deadnodes:
                deadnodes.append(node)


def synchronize(node):
    requests.get("http://" + node + "/init")
    file_tree.recursive_recover(file_tree.root, node, '/')

@app.route('/init')
def init():
    global file_tree
    global datanodes
    global deadnodes
    file_tree = FileTree()
    result = 0

    for datanode in datanodes:
        try:
            response = requests.get("http://" + datanode + "/init")
        except requests.exceptions.RequestException:
            continue
        result += int(response._content.decode())
    deadnodes = []
    return Response(status=200, response=str(result // 3))


@app.route('/create')
def create():
    file_path = request.headers.get('File-Name', type=str)
    datanode = random.choice(datanodes)
    while datanode in deadnodes and not len(datanodes) == len(deadnodes):
      datanode = random.choice(datanodes)
    # datanode = '10.91.91.190:5000'
    file_tree.add_node(file_path, False, list([datanode]))
    try:
        requests.get("http://" + datanode + "/create", headers={'File-Name': file_path})
    except requests.exceptions.RequestException:
        pass
    return Response(status=200)


@app.route('/read')
def read():
    file_path = request.headers.get('File-Name', type=str)
    nodes = file_tree.search_node(file_path)
    if nodes != []:
        return Response(status=200, response=json.dumps(nodes))
    return Response(status=400)


@app.route('/write')
def write():
    file_path = request.headers.get('File-Name', type=str)
    datanode = random.choice(datanodes)
    while datanode in deadnodes and not len(datanodes) == len(deadnodes):
      datanode = random.choice(datanodes)
    # datanode = '10.91.91.190:5000'
    file_tree.add_node(file_path, False, list([datanode]))
    return Response(status=200, response=datanode)


@app.route('/delete_file')
def delete_file():
    file_path = request.headers.get('File-Name', type=str)
    if not file_tree.file_exists(file_path):
        return Response(status=400, response="file doesn`t exist")
    return file_tree.delete_node(file_path, datanodes)


@app.route('/info')
def info():
    file_path = request.headers.get('File-Name', type=str)
    result = file_tree.info_node(file_path)
    return Response(status=200, response=json.dumps(result.json()))


@app.route('/copy')
def copy():
    file_path = request.headers.get('File-Name-Old', type=str)
    new_path = request.headers.get('File-Name-New', type=str)
    nodes = file_tree.search_node(file_path)
    if file_tree.search_node(new_path) != []:
        return Response(status=400)
    if file_tree.search_node(file_path) == []:
        return Response(status=400)
    nodes = file_tree.search_node(file_path)
    file_tree.add_node(new_path, False, nodes)
    for node in nodes:
        try:
            requests.get("http://" + node + "/copy", headers={'File-Name-Old': file_path, 'File-Name-New': new_path},
                         timeout=10)
        except requests.exceptions.RequestException:
            pass

    return Response(status=200)


@app.route('/replicate')
def replicate():
    file_path = request.headers.get('path', type=str)
    occupied = file_tree.search_node(file_path)
    if not occupied:
        return Response(status=400)
    for dn in datanodes:
        if dn not in occupied and dn not in deadnodes:
            file_tree.update_location(file_path, dn)
            return Response(status=200, headers={"address": dn})
    return Response(status=200)


@app.route('/move')
def move():
    file_path = request.headers.get('File-Name-Old', type=str)
    new_path = request.headers.get('File-Name-New', type=str)
    if file_tree.search_node(new_path) != []:
        return Response(status=400)
    if file_tree.search_node(file_path) == []:
        return Response(status=400)
    nodes = file_tree.search_node(file_path)
    file_tree.add_node(new_path, False, nodes)
    for node in nodes:
        try:
            requests.get("http://" + node + "/move", headers={'File-Name-Old': file_path, 'File-Name-New': new_path}
                         , timeout=10)
        except requests.exceptions.RequestException:
            pass

    file_tree.delete_node(file_path, datanodes)
    return Response(status=200)


@app.route('/cd')
def cd():
    directory = request.headers.get('Directory', type=str)
    if file_tree.directory_exists(directory) or directory == '/':
        return Response(status=200)
    else:
        return Response(status=400)


@app.route('/ls')
def ls():
    directory = request.headers.get('Directory', type=str)
    result = file_tree.ls(directory)
    if result == None:
        return Response(status=400)
    return Response(status=200, response=json.dumps(result))


@app.route('/mkdir')
def mkdir():
    directory = request.headers.get('Directory', type=str)
    file_tree.add_node(directory, True, datanodes)
    return Response(status=200)


@app.route('/delete_dir')
def delete_dir():
    directory = request.headers.get('Directory', type=str)
    if not file_tree.directory_exists(directory):
        return Response(status=400, response="directory doesn`t exist")
    file_tree.delete_node(directory, datanodes)
    return Response(status=200)


if __name__ == '__main__':
    # datanodes = ['10.91.91.190:5000', '10.91.91.190:5001']
    scheduler = BackgroundScheduler()
    replication_factor = 3
    job = scheduler.add_job(find_datanodes, 'interval', seconds=300)
    job = scheduler.add_job(heartbeat, 'interval', seconds=30)
    scheduler.start()
    app.run(host='0.0.0.0', port=80, debug=True, use_reloader=False)

