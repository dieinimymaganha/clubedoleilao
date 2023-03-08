import requests
import json

response = requests.post('https://www.dbsleiloes.com.br/app/lotes')

if response.status_code == 200:
    response = response.json()

    category = response['categorias']
    print(category)