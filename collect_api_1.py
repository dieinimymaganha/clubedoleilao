import requests
import json
import time


class CollectApi1:

    def __init__(self, list_sites):
        self.list_sites = list_sites
        self.list_lotes = []
        self.list_lote_formated = []

    def get_data(self):
        for link_site in self.list_sites:

            payload_category = {
                "page": 1,
                "pages": 1,
                "limit": "20",
                "limite": 20,
                "count": 0,
                "skip": 0,
                "tab": 1,
                "hoje": "",
                "vara": "",
                "busca": "",
                "categoria": "",
                "sub": "",
                "cidade": "",
                "origem": "tudo",
                "dominio": link_site['domain']
            }

            response = requests.post(f'{link_site["site"]}/categorias',
                                     json=payload_category)

            json_response_category = response.json()

            keys_json_response_category = json_response_category['c'].keys()
            list_payloads = []
            for key in keys_json_response_category:
                values = json_response_category['c'][key]
                list_sub_category = values['s']
                list_payloads += self.create_list_payloads(key,
                                                           list_sub_category,
                                                           link_site)

            self.get_list_lotes(link_site=link_site,
                                list_payloads=list_payloads)

    def get_list_lotes(self, link_site, list_payloads):
        for payload_category in list_payloads:
            response = requests.post(
                f'{link_site["site"]}/lotes',
                json=payload_category)
            if response.status_code == 200:
                lotes = response.json()['l']
                for lote in lotes:

                    if lote['status'].upper() == 'ABERTO':

                        lote.update({'link_site': link_site['site']})
                        lote.update(
                            {'categoria': payload_category['categoria'],
                             'sub_categoria': payload_category['sub']})

                        res_leilao = requests.get(
                            f'{link_site["site"]}/pregao/leilao/{lote["leilao"]}')

                        res_lote = requests.get(
                            f'{link_site["site"]}/pregao/lote/{lote["id"]}')

                        if res_leilao.status_code == 200:
                            res_leilao = res_leilao.json()
                            res_leilao = res_leilao['l']
                            res_leilao = {'res_leilao': res_leilao}
                            lote.update(res_leilao)

                        if res_lote.status_code == 200:
                            res_lote = res_lote.json()
                            res_lote = res_lote['l']
                            res_lote = {'res_lote': res_lote}
                            lote.update(res_lote)

                        self.list_lotes.append(lote)

    @staticmethod
    def create_list_payloads(key, list_sub_category,
                             link_site):

        list_payloads = []
        for sub in list_sub_category:
            if 'page' in sub:
                continue
            qtd = sub['q']
            sub_category = sub['s']
            payload_category = {
                "page": 1,
                "pages": 1,
                "limit": str(qtd),
                "limite": qtd,
                "count": 0,
                "skip": 0,
                "tab": 1,
                "hoje": "",
                "vara": "",
                "busca": "",
                "categoria": key,
                "sub": sub_category,
                "cidade": "",
                "origem": "tudo",
                "dominio": link_site['domain']
            }

            list_payloads.append(payload_category)
        return list_payloads

    def format_json(self):
        for lote in self.list_lotes:
            name = lote['nome']
            sub_category = lote['sub_categoria']
            categoty = lote['categoria']

            if lote['image'] != '':
                cover = 'https://asta.nyc3.cdn.digitaloceanspaces.com/' + lote[
                    'image']
            else:
                cover = ''
            link = lote['link_site'] + '/pregao/' + lote['leilao'] + '/' + \
                   lote['id']

            city = lote['res_lote']['d']['cidade']
            uf = lote['res_lote']['d']['uf']

            if uf is not None:
                uf = uf.upper()

            valor = lote['valor']
            description = lote['res_lote']['descricao']

            files = lote['res_lote']['anexos']
            list_images = []

            for file in files:
                if 'image' in file['type']:
                    image = 'https://asta.nyc3.cdn.digitaloceanspaces.com/' + \
                            file[
                                'path'] + file['arquivo']

            site = lote['link_site']

            start_at = lote['res_leilao']['datas']['d1']

            start_second_at = lote['res_leilao']['datas']['d2']

            inscante = lote['res_leilao']['praca']

            json_lote = {
                "name": name,
                "category": categoty,
                "subCategory": sub_category,
                "cover": cover,
                "endAt": "",
                "instance": inscante,
                "link": link,
                "city": city,
                "state": uf,
                "value": valor,
                "description": description,
                "images": list_images,
                "companyID": site,
                "startAt": start_at,
                "approved": True,
                "endFirstAt": "",
                "startSecondAt": start_second_at

            }
            self.list_lote_formated.append(json_lote)

    def write_json_final(self):
        with open("api_1_formated.json", "w") as arquivo:
            json.dump(self.list_lote_formated, arquivo, ensure_ascii=False)

    def write_json_all(self):
        with open("api_1.json", "w") as arquivo:
            json.dump(self.list_lotes, arquivo, ensure_ascii=False)

    @classmethod
    def run_collect_api_1(cls, list_sites):
        run = cls(list_sites=list_sites)
        run.get_data()
        run.format_json()
        run.write_json_final()
        run.write_json_all()


LISTA = [{'site': 'https://www.baldisseraleiloeiros.com.br',
          'domain': 'baldissera'},
         {'site': 'https://www.fbleiloes.com.br', 'domain': 'becker'},
         {'site': 'https://www.krobelleiloes.com.br', 'domain': 'krobel'},
         {'site': 'https://www.catarinaleiloes.com.br', 'domain': 'leiloador'},
         {'site': 'https://www.licitari.com.br', 'domain': 'licitari'},
         {'site': 'https://www.topleiloes.com.br', 'domain': 'pizzolatti'},
         {'site': 'https://www.sampaioleiloes.com.br', 'domain': 'sampaio'},
         {'site': 'https://www.zampierileiloes.com.br', 'domain': 'zampieri'},
         {'site': 'https://maxterleiloes.com.br', 'domain': 'leiloador'},
         {'site': 'https://www.leiloesrei.com.br', 'domain': ''}
         ]

start_time = time.time()
CollectApi1.run_collect_api_1(list_sites=LISTA)
end_time = time.time()
total_time = end_time - start_time
hours, rem = divmod(total_time, 3600)
minutes, seconds = divmod(rem, 60)

print(
    f"Tempo de execução: {int(hours):02d}h {int(minutes):02d}m {int(seconds):02d}s")
