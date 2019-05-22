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

id = 0

transactions_queue = []

block_chain = [genesis_block]

difficulty_bits = 15

target = 2 ** (256-difficulty_bits)

hostname = socket.gethostname()

miners = [{"ip":"localhost","port":"5003","hostname":"Pi02_miner_1"}]

peer_nodes = []

sync_chain = []

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

@app.route('/syncTime',methods=['POST'])
def syncTime():
    sync_stat =  json.loads(request.data.decode("utf-8"))    
    start_stop_miners(sync_stat)
    send_chain_to_peers()        
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

def start_stop_miners(sync):
    global miners
    http = httplib2.Http()
    for i in miners:        
        http.request("http://{}:{}/sync_flag".format(i["ip"],i["port"]),"POST",json.dumps(sync))



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
    res, nodes = http.request('http://192.168.2.105:5000/nodeAnnounce',"POST",json.dumps(data))
    

@app.route('/chainSync',methods=['POST'])
def chainSync():
    global sync_chain
    chain =  json.loads(request.data.decode("utf-8"))
    sync_chain.append(chain)    
    if(len(sync_chain) == len(peer_nodes)-1):
        synchronize()      
    return "OK",200

@app.route('/peerFound',methods=['POST'])
def peerFound():
    global peer_nodes
    nodes =  json.loads(request.data.decode("utf-8"))
    peer_nodes = nodes
    print(peer_nodes)   
    return "OK",200

def synchronize():    
    global sync_chain,block_chain,hostname
    hosts_sync_dic = {
        "Pi01": 4,
        "Pi02": 3,
        "Pi03": 2,
        "Pi04": 1
    }
    sync_chain.append({"chain":block_chain,"hostname":hostname})
    len_chains = []
    hosts = []
    for i in sync_chain:
        len_chains.append(len(i["chain"]))
        hosts.append(i["hostname"])
    longest = len_chains[0]
    hostest = hosts[0]
    longest_chain_index = 0
    for i in range(1,len(len_chains)):
        if(len_chains[i] > longest):
            longest = len_chains[i]
            hostest = hosts[i]
            longest_chain_index = i
        elif(len_chains[i] == longest):
            if(hosts_sync_dic[hostest] < hosts_sync_dic[hosts[i]]):
                longest = len_chains[i]
                hostest = hosts[i]
                longest_chain_index = i
    block_chain = sync_chain[longest_chain_index]["chain"]
    print("longest chain is from host {}".format(hosts[longest_chain_index]))
    sync_chain = []
    http = httplib2.Http()
    http.request("http://192.168.2.105:5000/syncDone","GET")
    

def send_chain_to_peers():
    global peer_nodes,hostname,block_chain
    http = httplib2.Http()
    for i in peer_nodes:
        if(i["hostname"] != hostname):
            data = {
                "chain":block_chain,
                "hostname":hostname
            }
            http.request("http://{}:{}/chainSync".format(i["ip"],i["port"]),"POST",json.dumps(data))



if __name__ == '__main__':
    initialize()
    app.run(host='0.0.0.0',port='5000')