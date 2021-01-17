# !/usr/bin/python
# -*- coding: utf-8 -*-

# тесты для проверки работоспособности


import requests
import matplotlib.pyplot as plt
import networkx as nx

url_all = 'http://127.0.0.1:8080/all'
url_add = 'http://127.0.0.1:8080/add'
url_info = 'http://127.0.0.1:8080/info/test'
url_del = 'http://127.0.0.1:8080/del/test'

# test 1:
req_all = requests.get(url=url_all)
req_all.encoding = 'utf-8'
print(url_all, req_all.json())

# test 2:
headers_add = {'content-type': 'application/json'}
data_add = {"def": "определение", "head": "test", "headru": "тест"}
req_add = requests.post(url=url_add, data=str(data_add).encode('utf-8'), headers=headers_add)
req_add.encoding = 'utf-8'
print(url_add, req_add.json())

# test 3:
req_info = requests.get(url=url_info)
req_info.encoding = 'utf-8'
print(url_info, req_info.json())

# test 4:
req_del = requests.get(url=url_del)
req_del.encoding = 'utf-8'
print(url_del, req_del.json())

# test 5:
# graph = nx.Graph()
# gloss = 'Глоссарий'
# graph.add_edge(gloss, 'API')
# graph.add_edge(gloss, 'TEST')
# graph.add_edge(gloss, 'AAA')
# graph.add_edge(gloss, 'BBB')
# nx.draw(graph, with_labels=True, font_weight='bold')
# plt.show()
