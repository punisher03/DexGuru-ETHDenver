
import requests
import json
import re
import time
from flask import Flask
from flask import request
from flask import Response
from flask_sslify import SSLify
from tg_api import TgApi
from Commands import Commands
import tokens
import pickle
from formating import format_price

headers = {'api-key':tokens.dexguru_token}
chainMapping = {'ethereum':1,'bsc':56,'polygon':137,'avalanche':43114,'arbitrum':42161,'fantom':250,'celo':42220,'optimism':10}


class Dexguru(object):

    def write_json(self,data,filename='response.json'):
        with open(filename, 'w') as f:
            json.dump(data,f,indent=4,ensure_ascii=False)


    def get_address_from_ticker(self,coin, chainId):
        try:
            url="http://api.dev.dex.guru/v1/chain/{chain_id}/tokens".format(chain_id=chainId)
            params = {'search_string':coin}
            r = requests.get(url, headers=headers, params=params, verify=False).json()
            return r['data'][0]['address']
        except:
            return "Wrong data"

    def get_coin_price(self,coin, chainId):
        print("In get c price")
        try:
            address= self.get_address_from_ticker(coin, chainId)
            url = "https://api.dev.dex.guru/v1/chain/{chain_id}/tokens/{token_address}/market".format(chain_id=chainId,token_address=address)
            r = requests.get(url, headers=headers, verify=False).json()
            #write_json(r)
            return r['price_usd']
        except:
            print("returning -1 price")
            return -1

    def get_coin_volume(self,coin, chainId):
        print("In get c volume")
        try:
            address= self.get_address_from_ticker(coin, chainId)
            url = "https://api.dev.dex.guru/v1/chain/{chain_id}/tokens/{token_address}/market".format(chain_id=chainId,token_address=address)
            r = requests.get(url, headers=headers, verify=False).json()
            #write_json(r)
            return [r['volume_24h_usd'],r['volume_24h_delta']]
        except:
            print("returning -1 volume")
            return [-1,-1]

    def parse_message(self,message):
        if 'edited_message' in message:
            return "alert"
        print("In parse message")
        print("Parse message",message)
        chat_id = message['message']['chat']['id']
        txt = message['message']['text']
        if txt[1:] == 'alerts':
            self.commands.alerts(chat_id)
            return "alert"
        elif txt[1:] == 'clear':
            self.commands.clear(chat_id)
            return "alert"
        else:
            decider = txt.split(",")
            if len(decider)==3:
                try:
                    pattern = r'^[\/][a-zA-Z]+(\,[a-zA-Z]+)+$'
                    ticker = re.findall(pattern, txt)
                    print(ticker)

                    if ticker:
                        print(txt)
                        param,chain,coin=txt.split(",")
                        chainid=chainMapping[chain.lower()]
                    else:
                        chainid = 0
                        coin=''
                    return chat_id,param[1:],chainid,coin
                except:
                    print("returning null parse message")
                    return chat_id,'',0,''
            elif len(decider)==4:
                self.commands.higher_lower(chat_id,txt)
                return "alert"
            else:
                return ["Wrong Data",chat_id]

    def processAlerts(self):
        if 'alerts' not in self.db:
            return
        higher = 'HIGHER'
        lower = 'LOWER'
        alerts = self.db['alerts']
        toRemove = []
        for chatId in alerts:
            for chain in alerts[chatId]:
                coins = alerts[chatId][chain]
                for coin in coins:
                    ops=coins[coin]
                    for op in ops:
                        targets = ops[op]
                        price = self.get_coin_price(coin,chainMapping[chain.lower()])
                        for target in targets:
                            if op == lower and price < target or op == higher and price > target:
                                self.api.sendMessage(f"{coin} is {'below' if op == lower else 'above'} {format_price(target)} at {format_price(price)} ", chatId)
                                toRemove.append((chatId,chain, coin, op, target))

        for tr in toRemove:
            self.removeAlert(tr[0], tr[1], tr[2], tr[3], tr[4])


    def removeAlert(self, chatId, chain, coin, op, target):
        alerts = self.db['alerts']
        alerts[chatId][chain][coin][op].remove(target)
        if len(alerts[chatId][chain][coin][op]) == 0:
            alerts[chatId][chain][coin].pop(op)
            if len(alerts[chatId][chain][coin]) == 0:
                alerts[chatId][chain].pop(coin)
                if len(alerts[chatId][chain]) == 0:
                    alerts[chatId].pop(chain)
                    if len(alerts[chatId]) == 0:
                        alerts.pop(chatId)


    def send_message(self,chat_id, text):
        url='https://api.telegram.org/bot{token}/sendMessage'.format(token=tokens.TG_TOKEN)
        payload = {'chat_id':chat_id , 'text':text}
        r=requests.post(url, json=payload)
        return r

    # @app.route('/',methods=['POST','GET'])
    # def index():
    #     if request.method=='POST':
    #         msg=request.get_json()
    #         chat_id,chainid,coin = parse_message(msg)
    #
    #         if not coin:
    #             print("not coin")
    #             send_message(chat_id,'Wrong data')
    #             return Response('ok', status=200)
    #
    #         price = get_coin_price(coin,chainid)
    #         if price == -1:
    #             print("price -1")
    #             send_message(chat_id,'Wrong data')
    #             return Response('ok', status=200)
    #
    #         send_message(chat_id,price)
    #         #write_json(msg,'telegram_request.json')
    #         return Response('ok',status=200)
    #     else:
    #         return '<h1> DexGuru Bot</h1>'

    def sendmessage(self,msg):
        for ms in msg:
            self.last_update = ms['update_id']
            if self.parse_message(ms) == "alert":
                return
            elif self.parse_message(ms)[0] == "Wrong Data":
                self.send_message(self.parse_message(ms)[1],'Wrong data')
                return
            else:
                chat_id,param,chainid,coin = self.parse_message(ms)
                print(ms)
                if param=="price":
                    price = self.get_coin_price(coin,chainid)
                    if price == -1:
                        self.send_message(chat_id,'Wrong data')
                    else:
                        self.send_message(chat_id,price)
                elif param=="volume":
                    volume,volume_delta = self.get_coin_volume(coin,chainid)
                    if volume == -1:
                        self.send_message(chat_id,'Wrong data')
                    else:
                    
                        format_message = f'24hr volume of {coin} in USD is {volume}\n24hr volume delta of {coin} in USD is {volume_delta}'
                        self.send_message(chat_id,format_message)



    def persist_db(self):
        with open(tokens.DB_FILENAME, 'wb') as fp:
            pickle.dump(self.db, fp)


    def run(self,debug=True):
        self.last_update=0
        self.api=TgApi()
        try:
            with open(tokens.DB_FILENAME, 'rb') as fp:
                self.db = pickle.load(fp)
        except:
            print("error loading db, defaulting to empty db")
            self.db = {}
        print("db at start: {}".format(self.db))
        self.commands = Commands(self.db,self.api)
        while(True):
            msg=self.api.getUpdates(self.last_update)


            self.sendmessage(msg)
            self.processAlerts()
            time.sleep(1)
            self.persist_db()



# https://api.telegram.org/bot5162481471:AAFMF1P1r6-m_QOjb8TqmOO1nQWY9s-bvRM/getMe
# https://api.telegram.org/bot5162481471:AAFMF1P1r6-m_QOjb8TqmOO1nQWY9s-bvRM/sendMessage?chat_id=707549658&text=Hey man
# https://api.telegram.org/bot5162481471:AAFMF1P1r6-m_QOjb8TqmOO1nQWY9s-bvRM/setWebhook?url=https://rish003.pythonanywhere.com/


if __name__ == '__main__':
    #main()
    app = Dexguru()
    app.run()
