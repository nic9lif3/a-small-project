import csv
from urllib import parse
from glob import glob
import numpy as np
lines = []
with open("anomalous_txt.txt") as att:
    for line in att:
        if line is '\n':
            continue
        else:
            lines.append(line.strip())
records = []
idx = 0
for x in range(0, len(lines)-1):
    if "GET" in lines[x] or "POST" in lines[x]:
        data = {
            "ID": idx
        }
        parts = lines[x].split(' ')
        if "GET" in parts[0]:
            url = parts[1].split('?')
            data.update({
                "METHOD": "GET",
                "URL": url[0],
            })
            if len(url) != 1:
                data.update({"QUERY": url[1]})
            else:
                data.update({"QUERY": ""})
        if "POST" in parts[0]:
            data.update({
                "METHOD": "POST",
                "URL": parts[1],
                "QUERY": lines[x+13]
            })
        data.update({
            "ID": idx,
            "USER-AGENT": lines[x+1],
            "PRAGMA": lines[x+2],
            "CACHE-CONTROL": lines[x+3],
            "ACCEPT": lines[x+4],
            "ACCEPT-ENCODING": lines[x+5],
            "ACCEPT-CHARSET": lines[x+6],
            "ACCEPT-LANGUAGE": lines[x+7],
            "HOST": lines[x+8],
            "COOKIE": lines[x+9],
            "CONNECTION": lines[x+10]
        })
        records.append(data)
        idx += 1
blacklist=dict()
for f in glob('Blacklist\*txt'):
    name=f.split('\\')[-1][:-4]
    with open(f,'r') as fi:
        blacklist[name]=fi.read().splitlines()
def process_query(query):
    while True:
        pre_query=query
        query=parse.unquote(query)
        if pre_query==query:
            break
    ##Xac dinh query co chua back list va blacklist loai nao
    query_bl=[-1]*len(blacklist.keys())
    for i,bl in enumerate(blacklist.keys()):
        for j,bli in enumerate(blacklist[bl]):
            if bli in query.lower():
                query_bl[i]=j

    ##Xac dinh min, max, mean cua key, value
    parameters=query.split('&')
    k_length=[-1,-1,-1]
    v_length=[-1,-1,-1]
    key_length=list()
    value_length=list()
    for parameter in parameters:
        if parameter=='':
            continue
        find=parameter.find('=')
        key,value=parameter[:find],parameter[find:]
        key_length.append(len(key))
        value_length.append(len(value))
    if len(key_length) >0 and len(value_length)>0:
        k_length=[np.max(key_length),np.min(key_length),np.mean(key_length)]
        v_length=[np.max(value_length),np.min(value_length),np.mean(value_length)]
 
    ##Dem tan suat xuat hien cua cac chu cai trong value

    a,b=np.unique(list(query),return_counts=True)
    a=[i.encode('utf8') for i in a]
    c=dict(zip(a,b))

    return {
        'q':query,
        'bl':query_bl,
        'length':[k_length,v_length],
        'count':c
    }

with open("anomalous_txt.csv", 'w') as csv_file:
    fieldnames = ["ID", "METHOD", "URL", "QUERY",'PROCESS QUERY','BLACK LIST','KEY LENGTH','VALUE LENGTH','COUNT']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
    writer.writeheader()
    for record in records:
        info=process_query(record["QUERY"])
        writer.writerow({"ID": record["ID"], "METHOD": record["METHOD"], "URL": record["URL"], "QUERY": record["QUERY"],'PROCESS QUERY':info['q'].encode('utf-8'),'BLACK LIST':info['bl'],'KEY LENGTH':info['length'][0],'VALUE LENGTH':info['length'][1],'COUNT':info['count']})

