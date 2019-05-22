from flask import Flask,request  
import json
import hashlib
import threading
import httplib2
import socket
app=Flask(__name__)




genesis_block = {
    "index":0,
    "title":"Genesis Block",
    "description":"",
    "icon":"http://192.168.2.105:5005/bkchn.png",
    "pbh":"000",
    "pow":"000",
    "hash":"gene3isb70c8",
    "timestamp":"000000000",
    "hostname":"piX",
    "txions":[{
        "title":"No transactions",
        "description":"This is the Genesis Block"
    }]

}

hosts_dic = {
    "Pi01":"192.168.2.101",
    "Pi02":"192.168.2.102",
    "Pi03":"192.168.2.103",
    "Pi04":"192.168.2.104"
}

id=0

transactions_queue = []

block_chain = [genesis_block]

difficulty_bits = 15

target = 2 ** (256-difficulty_bits)

hostname = socket.gethostname()

miners = [{"ip":"localhost","port":"5003","hostname":"Matrix-N_miner_1"},{"ip":"localhost","port":"5004","hostname":"Matrix-N_miner_2"},{"ip":"localhost","port":"5005","hostname":"Matrix-N_miner_3"}]

peer_nodes = []

@app.route('/jobs',methods=['POST'])
def jobs():
    global transactions_queue
    received_jobs = json.loads(request.data.decode('utf-8'))
    transactions_queue += received_jobs
    # print("jobs added")
    print("job queue length is {}".format(len(transactions_queue)))

    return "OK", 200

@app.route('/giveJob',methods=['GET'])
def giveJob():
    global transactions_queue
    if len(transactions_queue) > 0:
        job = {
            "txions":transactions_queue[0],
            "pbh": block_chain[len(block_chain)-1]["hash"],
            "index":block_chain[len(block_chain)-1]["index"],
            "stat":"Go"
        }
        del transactions_queue[0]
    else:
        job = {
           "stat":"None"
        }
    
    return json.dumps(job)
    
@app.route('/blockFound_miner',methods=['POST'])
def blockFound_miner():
    block =  json.loads(request.data.decode("utf-8"))
    stat = validate_block(block)
    if(stat == "Success"):
        threading.Thread(target=updateMiners,args=(block['hostname'],)).start()        
    return "OK",200


@app.route('/getID',methods=['GET'])
def send_ID():
    global id
    id=id+1
    return socket.gethostname()+"_miner_{}".format(id)

def updateMiners(minerID):
    http = httplib2.Http()
    data = {
        "hash":block_chain[len(block_chain)-1]["hash"]
    }
    for i in miners:
        if(i['hostname'] == minerID):            
            pass
        else:
            http.request("http://{}:{}/latestHash".format(i["ip"],i["port"]),"POST",json.dumps(data))


def validate_block(block):
    global block_chain
    transactions = block['txions']
    nonce = block['pow']
    prev_hash = block_chain[len(block_chain)-1]["hash"]
    timestamp = block["timestamp"]          
    hash_calc =  hashlib.sha256(str.encode(str(transactions) +str(nonce)+ str(prev_hash)+ str(timestamp))).hexdigest()
    if int(hash_calc, 16) < target:
        block_chain.append(block)
        # print("CHAIN LENGTH {}".format(len(block_chain)))   
        print(block['index'])   
        return "Success"
    else:
        transactions_queue.append(block["txions"])
        print("Transactions added back to the queue")
        return "Fail"

def initialize():
    global hostname,peer_nodes
    http = httplib2.Http()
    data = {
        "ip": hosts_dic[hostname],
        "port":"5000",
        "hostname": hostname
    }
    res, nodes = http.request('http://192.168.2.105:5000/nodeAnnounce',"POST",data)
    peer_nodes.append(json.loads(nodes.decode("utf-8")))

if __name__ == '__main__':
    initialize()
    app.run(host='0.0.0.0',port='5000')