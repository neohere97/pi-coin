from flask import Flask, request
import httplib2
import threading
import json

transactions_queue=[]
block_chain=[]
peer_nodes=[] 
latest_block=[]
validation_going_on=False
latest_validated_block_timestamp=0

stats = {
    "node_global_stats":{
        "total_blocks_mined":0,
        "avg_node_time":0,
        "miners":[]

    },
    "miner_containerName":{
        "blocks_successfully_mined":0,
        "avg_time":0,
        "current_block":{
            "verified_by":[]
        }

    }
}

app=Flask(__name__)

def monitor_queue_scale_miners():
    pass

def validate_block():
    pass
def announce_to_miners():
    pass
def announce_to_peer_nodes():
    #just announce to all the peers if a block is found
    pass

def announce_to_peer_nodes_thread():
    #will wait for response, after that read length of verification, check if all of them agree and signal the respective miner to go on or re do the old block
    pass

@app.route('/foundBlock_peer',methosds=['POST'])
def foundBlock_peer():
    pass

@app.route('/foundBlock_miner',methosds=['POST'])
def foundBlock_miner():
    pass

@app.route('/peerFound',methods=['POST'])
def peerFound():
    pass
@app.route('/moreJobs',methods=['POST'])
def moreJobs():
    pass

@app.route('/giveJob',methods=['GET'])
def giveJob():
    pass






if __name__ == '__main__':
    app.run(host='0.0.0.0',port='5000')
   