import requests
from lxml import etree
import grpc
from concurrent import futures
import currency_converter_pb2
import currency_converter_pb2_grpc
from api_keys.api_keys import VALID_API_KEYS

CURRENCY_URL = 'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-daily.xml'


def fetch_currency_rates():
    response = requests.get(CURRENCY_URL)
    if response.status_code == 200:
        xml_tree = etree.fromstring(response.content)
        namespace = {'ns': 'http://www.ecb.int/vocabulary/2002-08-01/eurofxref'}
        rates = xml_tree.xpath('//ns:Cube[@currency and @rate]', namespaces=namespace)
        rate_dict = {}
        for rate in rates:
            rate_dict[rate.attrib['currency']] = float(rate.attrib['rate'])
        rate_dict['EUR'] = 1.00
        return rate_dict
    else:
        print("Failed to fetch currency rates. Response: " + str(response.status_code))


def is_valid_api_key(api_key):
    return api_key in VALID_API_KEYS


class CurrencyConverter(currency_converter_pb2_grpc.CurrencyConverterServicer):
    def Convert(self, request, context):
        api_key = request.api_key
        base_currency = request.base_currency
        target_currency = request.target_currency
        amount = request.amount

        if not is_valid_api_key(api_key):
            context.abort(grpc.StatusCode.PERMISSION_DENIED, "Invalid API Key")

        if base_currency == target_currency:
            return currency_converter_pb2.ConversionResult(value=amount)

        rates = fetch_currency_rates()

        if base_currency not in rates or target_currency not in rates:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "Invalid currency codes.")

        base_rate = rates[base_currency]
        target_rate = rates[target_currency]
        value = (amount / base_rate) * target_rate

        return currency_converter_pb2.ConversionResult(value=value)


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    currency_converter_pb2_grpc.add_CurrencyConverterServicer_to_server(CurrencyConverter(), server)
    server.add_insecure_port('[::]:8080')
    server.start()
    print("Listening on localhost:8080")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()
