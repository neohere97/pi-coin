import httplib2
import threading
import json
import time


genesis_block = {
    "index":0,
    "title":"Genesis Block",
    "description":"",
    "icon":"http://192.168.2.105:5005/bkchn.png",
    "pbh":"000",
    "pow":"000",
    "hash":"gene3isb70c8",
    "timestamp":"000000000",
    "txions":[{
        "title":"No transactions",
        "description":"This is the Genesis Block"
    }]

}

main_chain = [genesis_block]
actual_chain = {
    "chain":main_chain
}

total_time = 0
time_last_block_added = 0
flag = 0

def validate_respond(block):
    global total_time,time_last_block_added,flag
    if(block["index"] - main_chain[len(main_chain)-1]["index"] == 1):
        main_chain.append(block)
        # update_peers()
        current_time = time.time()
        total_time = total_time + (current_time - time_last_block_added)
        time_last_block_added =current_time
        update_ui_blocks("chain")
        
        
        flag=flag+1
        if(flag == 5):
            flag=0
            update_ui_blocks("avg_time_per_block")
            
            
        return "Success"
        
    else:
        return "Fail"


def update_ui_blocks(param):    
    t= threading.Thread(target=update_ui_http,args=(param,))
    t.start() 

def update_ui_http(param):
    global main_chain    
    http = httplib2.Http()
    if(param == "chain"):
        http.request("http://192.168.2.105:1880/updateChain","POST",json.dumps(actual_chain))
    elif(param == "avg_time_per_block"):
        avg_time = total_time/len(actual_chain['chain'])
        print("Average Time = {}".format(avg_time))
        http.request("http://192.168.2.105:1880/avgTime","POST",str(avg_time))

    
