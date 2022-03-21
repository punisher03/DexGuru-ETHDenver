from formating import format_price

class Commands:
    def __init__(self,db,api):
        self.db=db
        self.api=api

    def higher_lower(self, chatId, command):
        parts = command.upper().split(",")
        if len(parts)!=5:
            self.api.sendMessage("Invalid command", chatId)
            return
        dataFlag=parts[0][1:]
        op = parts[1]
        chain = parts[2]
        coin = parts[3]
        try:
            target = float(parts[4])
        except ValueError:
            self.api.sendMessage('Invalid number "{}"'.format(parts[4]), chatId)
            return

        if 'alerts' not in self.db:
            self.db['alerts'] = {}
        alerts = self.db['alerts'][chatId] if chatId in self.db['alerts'] else {}
        if dataFlag in alerts:
            alert = alerts[dataFlag]
            if chain in alert:
                alert = alert[chain]
                if coin in alert and type(alert[coin]) is dict:
                    coinObj = alert[coin]
                    if op in coinObj:
                        coinObj[op].add(target)
                    else:
                        coinObj[op] = set([target])
                else:
                    alert[coin] = {op: set([target])}
            else:
                alert[chain] = {coin: {op: set([target])}}
        else:
            alerts[dataFlag] = {chain: {coin: {op: set([target])}}}
        self.db['alerts'][chatId] = alerts
        msg = f'Notification set for {dataFlag} of coin {coin} {"below" if op == "LOWER" else "above"} {format_price(target)} USD.'
        self.api.sendMessage(msg, chatId)

    def alerts(self, chatId):
        print("hi")
        if 'alerts' in self.db and chatId in self.db['alerts']:
            alertss=self.db['alerts'][chatId]
            print(alertss)
            msg = 'Current alerts:\n'
            for dataFlag in alertss:
                print(dataFlag)
                for chain in alertss[dataFlag]:
                    print(chain)
                    for coin in alertss[dataFlag][chain]:
                        for op in alertss[dataFlag][chain][coin]:
                            for target in alertss[dataFlag][chain][coin][op]:
                                msg=f'{msg}{coin} {op} {dataFlag} {target}\n'
            self.api.sendMessage(msg, chatId)
        else:
            self.api.sendMessage('No alert is set',chatId)

    def clear(self, chatId):
        if 'alerts' in self.db and chatId in self.db['alerts']:
            self.db['alerts'].pop(chatId)
        self.api.sendMessage('Done.',chatId)
