import requests
import tokens


class TgApi:
    TG_BASE_URL = "https://api.telegram.org"

    def getTgUrl(self, methodName):
        return f'{TgApi.TG_BASE_URL}/bot{tokens.TG_TOKEN}/{methodName}'

    def sendMessage(self, msg, chatid, parse_mode=None):
        print(f"sending msg to {chatid} '{msg}'")
        url = self.getTgUrl('sendMessage')
        r = requests.post(url=url, data={
            'chat_id': chatid,
            'text': msg,
            'parse_mode': parse_mode
        })
        return r

    def sendPhoto(self, fileName, caption, chatid, parse_mode=None):
        files = {'photo': open(fileName, 'rb')}
        url = self.getTgUrl('sendPhoto')
        r = requests.post(url=url, data={
            'chat_id': chatid,
            'caption': caption,
            'parse_mode': parse_mode,
        }, files= files)
        return r

    def getUpdates(self, last_update):
        offset = last_update+1
        url = self.getTgUrl('getUpdates')
        r = requests.post(
            url=url, data={'offset': offset, 'limit': 100, 'timeout': 9})
        updates = r.json()
        if not 'ok' in updates or not updates['ok']:
            return None
        return updates['result']
