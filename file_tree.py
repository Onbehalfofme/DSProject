import json
import random
import requests
from flask import Flask, Response


class FileTree:
    class Node:
        def __init__(self, name: str, is_dir: bool, parent=None, children: dict = {},
                     location: list = None):
            self.children = children
            self.parent = parent
            self.name = name
            self.is_dir = is_dir
            self.location = location

    def __init__(self):
        self.root = FileTree.Node('/', True, children={})

    def add_node(self, path: str, is_dir: bool, location: list):
        directories = path.split('/')[1:]
        current_node = self.root
        for dir in directories[:-1]:
            current_node = current_node.children.get(dir)
        current_node.children.update({directories[-1]: FileTree.Node(directories[-1], is_dir, parent=current_node, children={}, location=location)})

    def update_location(self, path: str, location: str):
        paths = path.split('/')[1:]
        current_node = self.root
        for p in paths:
            current_node = current_node.children.get(p)
        current_node.location.append(location)

    def search_node(self, path: str):
        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node != None:
            return current_node.location
        return []


    def delete_node(self, path: str, all_datanodes):
        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node != None:
            if not current_node.is_dir:
                datanodes = current_node.location
                for dn in datanodes:
                    request_delete(dn, path, current_node.is_dir)
            else:
                for dn in all_datanodes:
                    request_delete(dn, path, current_node.is_dir)
            current_node.parent.children.pop(current_node.name)
            return Response(200)
        else:
            return Response(status=400, response="doesn`t exist")

    def info_node(self, path: str):
        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node != None:
            return request_info(current_node.location[0], path)
        else:
            return {}

    def directory_exists(self, path: str):
        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node != None and current_node.is_dir == True:
            return True
        else:
            return False

    def file_exists(self, path: str):
        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node != None and current_node.is_dir == False:
            return True
        else:
            return False

    def ls(self, path: str):
        if path == "/":
            result = {}
            for node in self.root.children:
                name = node
                d = self.root.children[node].is_dir
                result.__setitem__(name, d)
            return result
        directories = path.split("/")[1:]
        current_node = self.root
        for dir in directories:
            current_node = current_node.children.get(dir)
        if current_node != None:
            result = {}
            for node in current_node.children:
                name = node
                d = current_node.children[node].is_dir
                result.__setitem__(name, d)
            return result
        else:
            return None

    def recursive_recover(self, current_level, datanode, path):
        if path != '/':
            path += '/'
        for node in current_level.children:
            current_node = current_level.children.get(node)
            if current_node.is_dir:
                self.recursive_recover(current_node, datanode, path + current_node.name)
            else:
                replica_servers = current_node.location
                if datanode in replica_servers:
                    replica_servers.remove(datanode)
                    if not replica_servers == []:
                        try:
                            requests.get("http://" + random.choice(replica_servers) + "/replicate",
                                         headers={'address': datanode, 'path': path + current_node.name})
                        except requests.exceptions.RequestException:
                            pass

def request_delete(datanode, path, is_dir):
    if is_dir:
        try:
            response = requests.get("http://" + datanode + "/rmdir", headers={'path': path})
        except requests.exceptions.RequestException:
            return Response(status=500)

    else:
        try:
            response = requests.get("http://" + datanode + "/delete", headers={'path': path})
        except requests.exceptions.RequestException:
            return Response(status=500)

    return response


def request_info(datanode, path):
    try:
        response = requests.get("http://" + datanode + "/info", headers={'path': path})
    except requests.exceptions.RequestException:
        return Response(status=500)

    return response
