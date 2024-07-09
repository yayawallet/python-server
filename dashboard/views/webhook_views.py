from adrf.decorators import api_view
from yayawallet_python_sdk.functions import verify
from .stream_response import stream_response

@api_view(['POST'])
async def notify_transaction(request):
    data = request.data
    signature = request.META.get('YAYA-SIGNATURE')
    response = verify.get_verified_payment_details(data, signature)
    print(response)
