import re
import time
import requests
import json


class CollectCentralSul:

    def __init__(self):
        self.list_responses = []
        self.list_formated = []

    def get_all_data(self):
        url = 'https://www.centralsuldeleiloes.com.br/api/auction?page=1'
        while True:
            response = requests.get(url)
            if response.status_code == 200:
                response = response.json()

                data = {"data": response['data']}
                for item in data['data']:
                    res_action = requests.get(
                        f'https://www.centralsuldeleiloes.com.br/api/auction-detran/{item["id"]}')
                    if res_action.status_code == 200:
                        res_action = res_action.json()

                        body = res_action['body']

                        if 'lots' in body:
                            for lot in body['lots']:
                                res_lot = requests.get(
                                    f'https://www.centralsuldeleiloes.com.br/api/lot/{lot["id"]}')
                                if res_lot.status_code == 200:
                                    lot.update({'res_lot': res_lot.json()})

                        item.update({'res_action': res_action})

                    data.update(item)

                self.list_responses.append(data)

                if response['next_page_url'] is not None:
                    url = response['next_page_url']
                else:
                    break

    @staticmethod
    def remove_html_css_js(text):
        # remove scripts
        text = re.sub(r'<script\b[^>]*>(.*?)<\/script>', '', text,
                      flags=re.S | re.M | re.I)

        # remove all html tags
        text = re.sub(r'<[^>]*>', '', text)

        # remove css styles
        text = re.sub(r'<style\b[^>]*>(.*?)<\/style>', '', text,
                      flags=re.S | re.M | re.I)
        text = re.sub(r'\n|\r|\t', '', text)
        text = re.sub(r'\{.*?\}', '', text)
        text = re.sub(r';', '', text)

        return text

    def formated_json(self):

        for itens in self.list_responses:
            for item in itens['data']:
                res_action = item['res_action']['body']
                for pos, lot in enumerate(res_action['lots']):
                    status = lot['status']['label']
                    if status.upper() == 'EM ABERTO':
                        start_at = lot['auction']['date1']
                        end_at = lot['auction']['date2']
                        title = lot['res_lot']['body']['title']
                        value = float(lot['res_lot']['body']['value'])
                        link = lot['url']
                        description = lot['res_lot']['body']['description']
                        description = self.remove_html_css_js(description)
                        category = lot['categories'][0]['label']
                        city = item['city']['name']
                        state = 'SC'
                        images = []

                        for image in lot['photos']:
                            images.append(image['image_url'])

                        cover = item['cover_photo']['image_url']

                        json_lote = {
                            "name": title,
                            "categoryId": category,
                            "cover": cover,
                            "endAt": end_at,
                            "instance": pos,
                            "link": link,
                            "city": city,
                            "state": state,
                            "value": value,
                            "description": description,
                            "images": images,
                            "companyID": 4,
                            "startAt": start_at,
                            "approved": True,
                            "endFirstAt": "",
                            "startSecondAt": ""
                        }
                        self.list_formated.append(json_lote)

    def write_json(self):
        with open("central_sul.json", "w") as arquivo:
            json.dump(self.list_responses, arquivo, ensure_ascii=False)

    def write_json_final(self):
        with open("central_sul_formated.json", "w") as arquivo:
            json.dump(self.list_formated, arquivo, ensure_ascii=False)

    @classmethod
    def run_collect(cls):
        run = cls()
        run.get_all_data()
        run.write_json()
        run.formated_json()
        run.write_json_final()


start_time = time.time()
CollectCentralSul.run_collect()

end_time = time.time()
total_time = end_time - start_time
hours, rem = divmod(total_time, 3600)
minutes, seconds = divmod(rem, 60)

print(
    f"Tempo de execução: {int(hours):02d}h {int(minutes):02d}m {int(seconds):02d}s")
