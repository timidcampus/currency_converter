from zeep import Client

client = Client('http://127.0.0.1:8080/?wsdl')
result = client.service.convert('apikey1', 'JPY', 'CHF', '500')
print("500 JPY in CHF is " + str(result))