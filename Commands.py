from formating import format_price

class Commands:
    def __init__(self,db,api):
        self.db=db
        self.api=api

    def higher_lower(self, chatId, command):
        parts = command.upper().split(",")
        if len(parts)!=4:
            self.api.sendMessage("Invalid command", chatId)
            return
        op = parts[0][1:]
        chain = parts[1]
        coin = parts[2]
        try:
            target = float(parts[3])
        except ValueError:
            self.api.sendMessage('Invalid number "{}"'.format(parts[2]), chatId)
            return

        if 'alerts' not in self.db:
            self.db['alerts'] = {}
        alerts = self.db['alerts'][chatId] if chatId in self.db['alerts'] else {}
        if chain in alerts:
            alert = alerts[chain]
            if coin in alert and type(alert[coin]) is dict:
                coinObj = alert[coin]
                if op in coinObj:
                    coinObj[op].add(target)
                else:
                    coinObj[op] = set([target])
            else:
                alert[coin] = {op: set([target])}
        else:
            alerts[chain] = {coin: {op: set([target])}}
        self.db['alerts'][chatId] = alerts
        msg = f'Notification set for coin {coin} {"below" if op == "LOWER" else "above"} {format_price(target)} USD.'
        self.api.sendMessage(msg, chatId)

    def alerts(self, chatId):
        if 'alerts' in self.db and chatId in self.db['alerts']:
            alerts=self.db['alerts'][chatId]
            msg = 'Current alerts:\n'
            for chain in alerts:
                for coin in alerts[chain]:
                    for op in alerts[chain][coin]:
                        for target in alerts[chain][coin][op]:
                            msg=f'{msg}{coin} {op} {target}\n'
            self.api.sendMessage(msg, chatId)
        else:
            self.api.sendMessage('No alert is set',chatId)

    def clear(self, chatId):
        if 'alerts' in self.db and chatId in self.db['alerts']:
            self.db['alerts'].pop(chatId)
        self.api.sendMessage('Done.',chatId)
