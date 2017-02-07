from bitcoin import *
import requests
import json

class BrainWallet:


    def spinUp(self, brainString):
        #print("brain wallet Importer")

        #self.brainPassword = input("Enter Brain Keychain: ")
        self.brainPassword = str(brainString)
        self.priv = sha256(self.brainPassword)
        self.pub = privtopub(self.priv)
        self.addr = pubtoaddr(self.pub)
        self.decoded_priv = decode_privkey(self.priv,'hex')
        self.wifPriv = encode_privkey(self.decoded_priv, 'wif')

        self.balance = requests.get('https://blockchain.info/q/addressbalance/'+ str(self.addr))
        self.balance = self.balance.text
        self.balance = float(self.balance)
        self.balance = self.balance / 100000

        # self.balance = unspent(self.addr)

        # self.balance = sum(self.balance)
    def spinTX(self, payee, amount, fee):
        utxo = unspent(self.addr)
        output = [{'value': amount, 'address': payee}]
        tx = mksend(utxo, output, self.addr, fee)
        tx_signed = sign(tx, 0 , self.priv)
        try:
            pushtx(tx_signed)
        except error as e:
            print('error sending transaction')
        if e:
            return 'failed'
        else: 
            return 'success'


        # try:
        #     self.balance = unspent(self.addr)
        #     print(self.balance)
        # except:
        #     print("0.000 BTC")



