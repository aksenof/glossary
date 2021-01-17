# !/usr/bin/python
# -*- coding: utf-8 -*-

# version: 1.0
# author: Andrey Aksenov

from flask import Flask, redirect, url_for, render_template, send_from_directory, request, Response, json
from flask_wtf import FlaskForm
from wtforms import SubmitField
import csv
import matplotlib.pyplot as plt
import networkx as nx
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret-key'  # секретный ключ для конфигурации
file = 'dictionary.csv'


def check_row(rows, tag_head):
    u"""
    :param rows: list of dicts
    :type rows: list
    :param tag_head: string
    :type tag_head: str
    :return: true or false
    :rtype: bool
    """
    for row in rows:
        if row.get('head') == tag_head:
            return True
    return False


def get_row(tag_head):
    current_row = {'error': 'tag not found'}
    with open(file, mode='r', encoding='utf8', newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter='|')
        for row in reader:
            current_row = dict(row)
            if current_row.get('head') == tag_head:
                return current_row
    return current_row


def get_all_rows():
    all_rows = []
    with open(file, mode='r', encoding='utf8', newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter='|')
        for row in reader:
            current_row = dict(row)
            all_rows.append(current_row)
    return all_rows


def add_row(data):
    with open(file, mode='a', encoding='utf8', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, delimiter='|', fieldnames=['head', 'headru', 'def'])
        writer.writerow(data)


def del_row(tag_head):
    error_row = {'error': 'tag not found'}
    # чтение:
    all_rows = []
    with open(file, mode='r', encoding='utf8', newline='') as csv_file:
        reader = csv.DictReader(csv_file, delimiter='|')
        for row in reader:
            current_row = dict(row)
            all_rows.append(current_row)
    # запись:
    if check_row(all_rows, tag_head):
        with open(file, mode='w', encoding='utf8', newline='') as csv_file:
            writer = csv.DictWriter(csv_file, delimiter='|', fieldnames=['head', 'headru', 'def'])
            writer.writeheader()
            deleted_data = {}
            for data in all_rows:
                if data.get('head') != tag_head:
                    writer.writerow(data)
                else:
                    deleted_data = data
            return {'status': 'OK', 'deleted': str(deleted_data)}
    else:
        return error_row


def prepare(string):
    u""" Предобработка строк для csv-файла
    :param string: string
    :type string: str
    :return: new_string
    :rtype: str
    """
    new_string = string.replace('|', '/')
    return new_string


def prepare_json(string):
    u""" Предобработка json для csv-файла
    :param string: string
    :type string: str
    :return: new_string
    :rtype: str
    """
    new_string = string.replace("\'", '\"')
    return new_string


def prepare_legend(dictionary):
    u""" Предобработка легенды для MindMap
    :param dictionary: dict
    :type dictionary: dict
    :return: new_string
    :rtype: str
    """
    new_string = "[{h}]: {ru} - {d}\n".format(h=dictionary.get('head', ''), ru=dictionary.get('headru', ''), d=dictionary.get('def', ''))
    return new_string


def prepare_node(node):
    u""" Предобработка вершин для MindMap
    :param node: dict
    :type node: dict
    :return: string
    :rtype: str
    """
    return node.get('head', '')


def gen_mind_map(all_data):
    if all_data:
        graph = nx.Graph()
        glossary = 'Глоссарий'
        nodes = [glossary]
        for data in all_data:
            if prepare_node(data) not in nodes:
                nodes.append(prepare_node(data))
        graph.add_nodes_from(nodes, color="green")
        for data in all_data:
            if (glossary, prepare_node(data)) not in graph.edges():
                graph.add_edge(glossary, prepare_node(data))
        nx.draw(graph, with_labels=True, font_weight='bold', font_size=6)
        if os.path.exists("static/mind_map.png"):
            os.remove("static/mind_map.png")
        plt.savefig("static/mind_map.png", format="png", dpi=150)
        plt.close()


class MyForm(FlaskForm):  # класс для формы с кнопкой "MindMap"
    submit = SubmitField('MindMap')


@app.route('/favicon.ico')
def favicon():  # значок для сайта
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/')
def go_to_index():  # переадресация на index
    return redirect(url_for('index'))


@app.route('/index', methods=['GET', 'POST'])
def index():  # то, что происходит в index
    form = MyForm()
    if form.is_submitted():
        return redirect(url_for('mind_map'))  # переход на страницу MindMap
    return render_template('index.html', form=form)


@app.route('/mind_map', methods=['GET', 'POST'])
def mind_map():
    all_data = get_all_rows()
    gen_mind_map(all_data)
    return render_template('mind_map.html', all_data=all_data)


@app.route('/all', methods=['GET'])
def all_info():
    try:
        resp_data = get_all_rows()
        return Response(json.dumps({'response': resp_data}), mimetype='text/plain')
    except Exception as e:
        return Response(json.dumps({'response': {'error': str(e)}}), mimetype='text/plain')


@app.route('/info/<head>', methods=['GET'])
def head_info(head):
    try:
        resp_data = get_row(head)
        return Response(json.dumps({'response': resp_data}), mimetype='text/plain')
    except Exception as e:
        return Response(json.dumps({'response': {'error': str(e)}}), mimetype='text/plain')


@app.route('/add', methods=['POST'])
def add_info():
    try:
        req = request.data.decode('utf-8')
        data = json.loads(prepare_json(req))
        add_row(data)
        return Response(json.dumps({'response': {'status': 'OK', 'added': str(data)}}), mimetype='text/plain')
    except Exception as e:
        return Response(json.dumps({'response': {'error': str(e)}}), mimetype='text/plain')


@app.route('/del/<head>', methods=['GET'])
def del_info(head):
    try:
        resp_data = del_row(head)
        return Response(json.dumps({'response': resp_data}), mimetype='text/plain')
    except Exception as e:
        return Response(json.dumps({'response': {'error': str(e)}}), mimetype='text/plain')


if __name__ == "__main__":
    app.run(host='127.0.0.1', port=8080)  # запуск приложения
