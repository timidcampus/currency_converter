import requests
from lxml import etree
from spyne import Application, rpc, ServiceBase, Unicode, Double
from spyne.protocol.json import JsonDocument
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication
from api_keys.api_keys import VALID_API_KEYS

CURRENCY_URL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'


def fetch_currency_rates():
    response = requests.get(CURRENCY_URL)
    if response.status_code == 200:
        xml_tree = etree.fromstring(response.content)
        namespace = {'ns': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
        rates = xml_tree.xpath('//ns:Cube[@currency and @rate]', namespaces=namespace) # more https://lxml.de/xpathxslt.html#the-xpath-method
        rate_dict = {}
        for rate in rates:
            rate_dict[rate.attrib['currency']] = float(rate.attrib['rate'])
        rate_dict['EUR'] = 1.00
        return rate_dict
    else:
        print("Failed to fetch currency rates. Response: " + str(response.status_code))


def is_valid_api_key(api_key):
    return api_key in VALID_API_KEYS


# http://spyne.io/#inprot=HttpRpc&outprot=JsonDocument&s=rpc&tpt=WsgiApplication&validator=true
class CurrencyConverterService(ServiceBase):
    @rpc(Unicode, Unicode, Unicode, Unicode, _returns=Double)
    def convert(ctx, api_key, base_currency, target_currency, amount): # ctx stands for context, mandatory due to spyne. holds info about request, e.g. client ip, http method etc.
        if not is_valid_api_key(api_key):
            raise ValueError("Invalid API Key")

        amount = float(amount)
        if base_currency == target_currency:
            return amount

        rates = fetch_currency_rates()

        if base_currency not in rates or target_currency not in rates:
            raise ValueError("Invalid currency codes.")

        base_rate = rates[base_currency]
        target_rate = rates[target_currency]

        return (amount / base_rate) * target_rate


application = Application(
    [CurrencyConverterService],
    'CurrencyConverter',
    in_protocol=Soap11(validator='lxml'),
    out_protocol=JsonDocument()
)

wsgi_application = WsgiApplication(application) # web server gateway interface - standard interface between web service and python web applications

if __name__ == '__main__':
    from wsgiref.simple_server import make_server

    server = make_server('127.0.0.1', 8080, wsgi_application)
    print("Listening on 127.0.0.1:8080")
    server.serve_forever()

