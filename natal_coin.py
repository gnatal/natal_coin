# Module 1 - Create a Blockchain

import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse 

# Block chain class
# Part 1 blockchain

# A crypto currenct is a blockchain that allows transactions
# Consensus for the blockchain (this is the trick)
# transactions does't go directly to a block, it goes to a mempool then it's loaded in the block
class Blockchain:

    def __init__(self):
        self.chain = []
        self.transactions = []
        self.createBlock(proof=1, previousHash='0')
        self.nodes = set()


    def createBlock(self, proof, previousHash, data={}):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': str(datetime.datetime.now()),
            'proof': proof,
            'data': {},
            'previousHash': previousHash,
            'transactions': self.transactions
        }
        self.transactions = []
        self.chain.append(block)
        return block

    def getPreviousBlock(self):
        return self.chain[-1]

    def proofOfWork(self, previousProof):
        newProof = 1
        validProof = False
        while validProof is False:
            hashOperation = hashlib.sha256(
                str(newProof**2 - previousProof**2).encode()).hexdigest()
            if hashOperation[0:4] == '0000':
                validProof = True
            else:
                newProof += 1
        return newProof

    def hash(self, block):
        encodedBlock = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encodedBlock).hexdigest()

    def isBlockchainValid(self, chain):
        blockIndex = 1
        previousBlock = chain[0]
        while blockIndex < len(chain):
            block = chain[blockIndex]
            if block['previousHash'] != self.hash(previousBlock):
                return False
            previousProof = self.proofOfWork(previousBlock['proof'])
            # here we check if the current proof generates a valid PoW
            proof = block['proof']
            hashOperation = hashlib.sha256(
                str(proof**2 - previousProof**2).encode()).hexdigest()
            if hashOperation[0:4] != '0000':
                return False
            previousBlock = chain[blockIndex]
            blockIndex += 1
        return True

    def addTransaction(self, sender, reciever, amount):
        self.transactions.append({
            'sender': sender,
            'receiver': receiver,
            'amount': amount
        })
        preivousBlock = self.getPreviousBlock()
        return preivousBlock['index'] + 1

    def addNode(self, address):
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)

    def replaceChain(self):
        network = self.nodes
        longestChain = None
        maxLength = len(self.chain)
        for node in network:
            response = requests.get(f'http://{node}/get_chain')
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                if length > maxLength and self.isBlockchainValid(chain):
                    longestChain = chain
                    maxLength = length
        if longestChain:
            self.chain = longestChain
            return True
        return False
        




# Web app
# mining
app = Flask(__name__)

# create an address for node on port 5000
node_address = str(uuid4()).replace('-','')

#create the blockchain
blockchain = Blockchain()
# blockchain.addNode(node_address)



@app.route('/mine_block', methods=['GET', 'POST'])
def mineBlock():
    preivousBlock = blockchain.getPreviousBlock()
    previousProof = preivousBlock['proof']
    previousHash = blockchain.hash(preivousBlock)
    blockchain.addTransaction(sender = node_address, receiver = 'natal', amount = 1000)
    proof = blockchain.proofOfWork(previousProof)
    block = blockchain.createBlock(previousHash=previousHash, proof=proof)
    response = {
        'message': 'Congratulations, you just mined a Block!',
        'index': block['index'],
        'timestamp': block['timestamp'],
        'proof': block['proof'],
        'data': block['data'],
        'transactions': block['transactions']
        'previousHahs': block['previousHash']
    }
    return jsonify(response), 200


@app.route('/get_chain', methods=['GET'])
def getChain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/is_valid', methods=['GET'])
def isValid():
    valid = blockchain.isBlockchainValid(blockchain.chain)
    if valid:
        return 'Blockchain valid'
    else:
        return 'Blockchain corrupted'


@app.route('/add_transaction', methods=['POST'])
def addTransaction():
    json = request.get_json()
    transactionsKeys = ['sender', 'receiver', 'amount']
    if not all (key in json for key in transactionsKeys)
        return 'Some elements are missing', 400
    index = blockchain.add_transaction(json['sender'], json['receiver'], json['amount'])
    response = {
        'message': f'This transaction will be added to block {index}'
    }
    return jsonify(response), 201
# Mine a block
app.run(host='0.0.0.0', port=4000)

## part 3 decentralize

# Connect new node
@app.route('/connect_node', methods=['POST'])
def connectNode():
    json = request.get_json()
    nodes = json.get('nodes')
    if nodes is None:
        return 'No nodes', 400
    for node in nodes:
        blockchain.addNode(node)
    response = {
        'message': 'All the nodes are now connected, natal coins has the following nodes: ',
        'total_nodes': list(blockchain.node)
    }
    return jsonify(response), 201

#Replace the chain by the longest chain
@app.route('/replace_chain', methods=['GET'])
def replaceChain():
    is_chain_replaced = blockchain.replaceChain()
    if is_chain_replaced:
        response = {
            'message': 'The node had different chains, so it was replaced',
            'newChain': blockchain.chain
        }
    else:
        response = {
            'message': 'all good, the chain is the largerst one',
            'actual_node': blockchain.chain
        }
    return jsonify(response), 200
