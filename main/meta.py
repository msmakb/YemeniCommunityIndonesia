import requests


class Whatsapp:

    def __init__(self) -> None:
        self.whatsapp_token = r"EAARUrUza86UBO9VISbnaR9Kckydf3ZCao7zpqzyoHuMY52xXUgwWWYve0mGAHth6J5g5yHmRinCZACPljbqlGI6rt9a6dDDnsvSFNALa7nAG4K4D8FJZAHSxKeVaZACrWekhXIZAjQ9iFiNrDkZAZBp88MR8DtXZAXtNThpxocMSh8PA3xVBHFSPL1U8BsbZAhy7uedVXQBocZAV3bVW2l0le9LgMdJgmqZALNAE9AZD"
        self.whatsapp_version = "v17.0"
        self.phone_number_id = "109155802081050"
        self.url = "https://graph.facebook.com"

    def sendTextMessage(self, message: str, to_phone_number) -> str:
        headers = {
            "Authorization": f"Bearer {self.whatsapp_token}",
            "Content-Type": "application/json",
        }
        url = f"{self.url}/{self.whatsapp_version}/{self.phone_number_id}/messages"
        data = {
            "messaging_product": "whatsapp",
            "to": to_phone_number,
            "type": "text",
            "text": {"body": message},
        }
        response = requests.post(url, json=data, headers=headers)
        print(f"whatsapp message response: {response.json()}")
