import grpc
import currency_converter_pb2
import currency_converter_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:8080')
    stub = currency_converter_pb2_grpc.CurrencyConverterStub(channel)

    api_key = 'apikey1'
    base_currency = 'USD'
    target_currency = 'EUR'
    amount = 250.0
    request = currency_converter_pb2.ConversionRequest(
        api_key=api_key,
        base_currency=base_currency,
        target_currency=target_currency,
        amount=amount
    )

    response = stub.Convert(request)

    print(f"Converted {amount} {base_currency} to {response.value} {target_currency}")


if __name__ == '__main__':
    run()
