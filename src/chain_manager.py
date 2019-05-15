import httplib2
import threading
import json

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


def validate_respond(block):
    if(block["index"] - main_chain[len(main_chain)-1]["index"] == 1):
        main_chain.append(block)
        update_ui_blocks()
        return "Success"
        
    else:
        return "Fail"


def update_ui_blocks():    
    t= threading.Thread(target=update_ui_http,args=("chain",))
    t.start() 

def update_ui_http(param):
    global main_chain    
    http = httplib2.Http()
    if(param == "chain"):
        http.request("http://192.168.2.105:1880/updateChain","POST",json.dumps(actual_chain))
    