from adrf.decorators import api_view
from ..models import ImportedDocuments, FailedImports, Contract, Scheduled, RecurringPaymentRequest
from ..serializers.serializers import ImportedDocumentsSerializer, FailedImportsSerializer, ScheduledSerializer, ContractSerializer, RecurringPaymentRequestSerializer
from ..constants import ImportTypes
from asgiref.sync import sync_to_async
from django.http.response import JsonResponse
import jwt

def get_imported_documents_serialized_data(db_results):
    serializer = ImportedDocumentsSerializer(db_results, many=True)
    return serializer.data

def get_failed_imports_serialized_data(db_results):
    serializer = FailedImportsSerializer(db_results, many=True)
    return serializer.data

def get_scheduled_serialized_data(db_results):
    serializer = ScheduledSerializer(db_results, many=True)
    return serializer.data

def get_contract_serialized_data(db_results):
    serializer = ContractSerializer(db_results, many=True)
    return serializer.data

def get_recurring_payment_request_serialized_data(db_results):
    serializer = RecurringPaymentRequestSerializer(db_results, many=True)
    return serializer.data

@api_view(['GET'])
async def proxy_report_list(request):
    auth_header = request.headers.get('Authorization')
    token = auth_header.split(' ')[1]
    decoded_token = jwt.decode(jwt=token, algorithms=["HS256"], options={'verify_signature':False})
    document_type = request.GET.get('document_type')
    imported_documents_by_type_obj = ImportedDocuments.objects.filter(import_type=ImportTypes[document_type], user_id=decoded_token.get("user_id"))
    imported_documents_by_type = await sync_to_async(get_imported_documents_serialized_data)(imported_documents_by_type_obj)
    return JsonResponse(imported_documents_by_type, safe=False)

@api_view(['GET'])
async def proxy_report_detail(request, id):
    imported_documents_by_id_obj = ImportedDocuments.objects.filter(uuid=id)
    imported_documents_by_id = await sync_to_async(get_imported_documents_serialized_data)(imported_documents_by_id_obj)
    import_type = imported_documents_by_id[0].get("import_type")
    failed_imports_obj = FailedImports.objects.filter(imported_document_id=id)
    failed_imports = await sync_to_async(get_failed_imports_serialized_data)(failed_imports_obj)
    uploaded = []
    on_queue = []
    if import_type == ImportTypes.get('SCHEDULED'):
        uploaded_obj = Scheduled.objects.filter(uploaded=True, imported_document_id=id)
        uploaded = await sync_to_async(get_scheduled_serialized_data)(uploaded_obj)
        on_queue_obj = Scheduled.objects.filter(uploaded=False, imported_document_id=id)
        on_queue = await sync_to_async(get_scheduled_serialized_data)(on_queue_obj)
    elif import_type == ImportTypes.get('CONTRACT'):
        uploaded_obj = Contract.objects.filter(uploaded=True, imported_document_id=id)
        uploaded = await sync_to_async(get_contract_serialized_data)(uploaded_obj)
        on_queue_obj = Contract.objects.filter(uploaded=False, imported_document_id=id)
        on_queue = await sync_to_async(get_contract_serialized_data)(on_queue_obj)
    elif import_type == ImportTypes.get('REQUEST_PAYMENT'):
        uploaded_obj = RecurringPaymentRequest.objects.filter(uploaded=True, imported_document_id=id)
        uploaded = await sync_to_async(get_recurring_payment_request_serialized_data)(uploaded_obj)
        on_queue_obj = RecurringPaymentRequest.objects.filter(uploaded=False, imported_document_id=id)
        on_queue = await sync_to_async(get_recurring_payment_request_serialized_data)(on_queue_obj)

    report = {
        'failed_count': len(failed_imports),
        'uploaded_count': len(uploaded),
        'on_queue_count': len(on_queue),
        'total_count': len(failed_imports) + len(uploaded) + len(on_queue),
        'failed': failed_imports,
        'uploaded': uploaded,
        'on_queue': on_queue,
    }

    return JsonResponse(report, safe=False)