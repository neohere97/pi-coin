from flask import Flask, request
import httplib2
import threading
import json
import hashlib

transactions_queue=[]

block_chain = []

peer_nodes=[] 

miners = [{"ip":"localhost","port":5001},
{"ip":"localhost","port":5002}]

difficulty_bits = 15

target = 2 ** (256-difficulty_bits)

app=Flask(__name__)

def monitor_queue_scale_miners():
    pass

def validate_block(block):    
    hash_calc =  hashlib.sha256(str.encode(str(block["txions"]) + str(block['pow'])+ str(block_chain[len(block_chain - 1)]["hash"])+ str(block['timestamp']))).hexdigest()
    if int(hash_calc, 16) < target:            
        return True
    else:
        return False                         
      
     
def announce_to_miners():
    pass

def send_block_thread():
    #will wait for response, after that read length of verification, check if all of them agree and signal the respective miner to go on or re do the old block
    pass

@app.route('/foundBlock_peer',methosds=['POST'])
def foundBlock_peer():

    pass

@app.route('/foundBlock_miner',methosds=['POST'])
def foundBlock_miner():
    global block_chain
    block_data = json.loads(request.data.decode('utf-8'))        
    res = validate_block(block_data)
    if(res):
        send_block(block_data)

    return "OK", 200
    

@app.route('/peerFound',methods=['POST'])
def peerFound():
    pass


@app.route('/moreJobs',methods=['POST'])
def moreJobs():
    pass

@app.route('/job',methods=['GET'])
def giveJob():
    global block_chain

    pass

@app.route('/latestHash',methods=['GET'])
def latestHash():
    global prev_hash
    return str(prev_hash)
    

def update_chain():
    global block_chain,prev_hash
    http = httplib2.Http()
    res, dat = http.request("http://localhost:5003/getNewChain","GET")
    block_chain = json.loads(dat)['chain']
    prev_hash = block_chain[len(block_chain)-1]['hash']


def send_block(block):    
    http = httplib2.Http()
    res, data = http.request('http://localhost:5003/blockFound',"POST", json.dumps(block))
    if(data.decode('utf-8') == "Fail"):
        update_chain()
        print(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5000')
   