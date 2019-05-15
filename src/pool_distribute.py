from flask import Flask, request
import httplib2
import threading
import json
import docker
import chain_manager

app=Flask(__name__)
chain = []
queue = []
transactions = []
lock = threading.Lock()

@app.route('/txion', methods=['POST'])
def txion():
    global queue,transactions    
    trans_received = json.loads(request.data.decode('utf-8'))
    if(len(transactions) == 8):
        queue.append(transactions)
        transactions = []
        print(len(queue))        
    transactions.append(trans_received)         
    return "OK", 200

@app.route('/gettxions', methods=['GET'])
def gettxions():
    global queue
    if(len(queue) != 0):
        job = queue[0]
        del queue[0]        
        print("transactions sent")
    else:
        job = {
            "txion":"None"
        }
    return json.dumps(job)   


if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5000')
   