import requests

url = "https://www.agencialeilao.com.br/"
response = requests.get(url)
html = response.text

print(html)