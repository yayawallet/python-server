from __future__ import absolute_import, unicode_literals

import celery
from datetime import datetime
from asgiref.sync import sync_to_async
from .models import Scheduled, Contract, FailedImports, RecurringPaymentRequest, ImportedDocuments
from yayawallet_python_sdk.api import scheduled, recurring_contract
from python_server.celery import app
from .async_task import async_task
from .serializers.serializers import ScheduledSerializer, ContractSerializer, RecurringPaymentRequestSerializer, FailedImportsSerializer
import json
from django.shortcuts import get_object_or_404
from .constants import ImportTypes

def process_date(start_at):
    if isinstance(start_at, datetime):
        return start_at.strftime("%d-%m-%Y")
    elif isinstance(start_at, str):
        return start_at
    else:
        return "1970-01-01"
    
def process_meta_data(meta_data):
    empty_obj = {}
    if meta_data:
        try:
            return json.loads(meta_data)
        except:
            return empty_obj
    else:
        return empty_obj

@async_task(app, bind=True)
async def import_scheduled_rows(self: celery.Task, data, id):
    for row in data:
        try:
            processed_date = process_date(row.get('start_at'))
            date_object = datetime.strptime(processed_date, "%d-%m-%Y")
            unix_timestamp = int(date_object.timestamp())
            instance = Scheduled(
                account_number=row.get('account_number'), 
                amount=row.get('amount'), 
                reason=row.get('reason'), 
                recurring=row.get('recurring'), 
                start_at=unix_timestamp, 
                meta_data=json.dumps(row.get('meta_data'), indent=4, sort_keys=True, default=str), 
                json_object=json.dumps(row, indent=4, sort_keys=True, default=str), 
                uploaded=False
            )
            imported_document = await sync_to_async(ImportedDocuments.objects.get)(pk=id)
            instance.imported_document_id = imported_document
            await sync_to_async(instance.save)()
        except Exception as error:
            print("An exception occurred, while importing scheduled payments!!", error)
            try:
                instance = FailedImports(json_object=json.dumps(row, indent=4, sort_keys=True, default=str), error_message=error)    
                imported_document = await sync_to_async(ImportedDocuments.objects.get)(pk=id)
                instance.imported_document_id = imported_document
                await sync_to_async(instance.save)()
            except Exception as error:
                print("An exception occurred, while saving failed scheduled payments!!", error)
    obj = await sync_to_async(Scheduled.objects.filter)(uploaded=False, imported_document_id=id)
    dep= await sync_to_async(get_scheduled_serialized_data)(obj)
    count = 0
    for row in dep:
        meta_data = {}
        if row.get('meta_data') != "" and row.get("meta_data") != None:
            meta_data = json.loads(row.get('meta_data'))
        if count >= 0:
            resp = await scheduled_row_upload({"account_number": row.get('account_number'), "amount": row.get('amount'), "reason": row.get('reason'), "recurring": row.get('recurring'), "start_at": row.get('start_at'), "meta_data": meta_data})
            if resp.status_code == 200 or resp.status_code == 201:
                scheduled_object = await sync_to_async(get_object_or_404)(Scheduled, pk=row.get('uuid'))
                scheduled_object.uploaded = True
                await sync_to_async(scheduled_object.save)()
            else:
                try:
                    content = ''
                    for chunk in resp.streaming_content:
                        if chunk:
                            content += chunk.decode('utf-8')
                    failed_instance = FailedImports(json_object="json.dumps(row, indent=4, sort_keys=True, default=str)", error_message=content)    
                    failed_imported_document = await sync_to_async(ImportedDocuments.objects.get)(pk=id)
                    failed_instance.imported_document_id = failed_imported_document
                    await sync_to_async(failed_instance.save)()
                except Exception as error:
                    print("An exception occurred, while saving failed schedule!!", error)

            
        count = count + 1

    failed_imports_obj = await sync_to_async(FailedImports.objects.filter)(imported_document_id=id)
    failed_imports = await sync_to_async(get_failed_imports_serialized_data)(failed_imports_obj)
    uploaded_obj = await sync_to_async(Scheduled.objects.filter)(uploaded=True, imported_document_id=id)
    uploaded = await sync_to_async(get_scheduled_serialized_data)(uploaded_obj)
    on_queue_obj = await sync_to_async(Scheduled.objects.filter)(uploaded=False, imported_document_id=id)
    on_queue = await sync_to_async(get_scheduled_serialized_data)(on_queue_obj)
    imported_document = await sync_to_async(ImportedDocuments.objects.get)(pk=id)
    imported_document.failed_count = len(failed_imports)
    imported_document.successful_count = len(uploaded)
    imported_document.on_queue_count = len(on_queue)
    await sync_to_async(imported_document.save)()


async def scheduled_row_upload(data):
    print(data)
    response = await scheduled.create(
        data.get('account_number'), 
        data.get('amount'), 
        data.get('reason'), 
        data.get('recurring'), 
        data.get('start_at'), 
        process_meta_data(data.get('meta_data'))
        )
    return response

def get_scheduled_serialized_data(db_results):
    serializer = ScheduledSerializer(db_results, many=True)
    return serializer.data

@async_task(app, bind=True)
async def import_contract_rows(self: celery.Task, data, id):
    for row in data:
        try:
            instance = Contract(
                contract_number=row.get('contract_number'), 
                service_type=row.get('service_type'), 
                customer_account_name=row.get('customer_account_name'), 
                meta_data=json.dumps(row.get('meta_data'), indent=4, sort_keys=True, default=str), 
                json_object=json.dumps(row, indent=4, sort_keys=True, default=str), 
                uploaded=False
            )
            imported_document = await sync_to_async(ImportedDocuments.objects.get)(pk=id)
            instance.imported_document_id = imported_document
            await sync_to_async(instance.save)()
        except Exception as error:
            print("An exception occurred, while importing contracts!!", error)
            try:
                instance = FailedImports(json_object=json.dumps(row, indent=4, sort_keys=True, default=str), error_message=error)    
                imported_document = await sync_to_async(ImportedDocuments.objects.get)(pk=id)
                instance.imported_document_id = imported_document
                await sync_to_async(instance.save)()
            except Exception as error:
                print("An exception occurred, while saving failed contracts!!", error)
    obj = await sync_to_async(Contract.objects.filter)(uploaded=False, imported_document_id=id)
    dep= await sync_to_async(get_contract_serialized_data)(obj)
    count = 0
    for row in dep:
        meta_data = {}
        if row.get('meta_data') != "" and row.get("meta_data") != None:
            meta_data = json.loads(row.get('meta_data'))
        if count >= 0:
            resp = await contract_row_upload({"contract_number": row.get('contract_number'), "service_type": row.get('service_type'), "customer_account_name": row.get('customer_account_name'), "meta_data": meta_data})
            if resp.status_code == 200 or resp.status_code == 201:
                contract_object = await sync_to_async(get_object_or_404)(Contract, pk=row.get('uuid'))
                contract_object.uploaded = True
                await sync_to_async(contract_object.save)()
            else:
                try:
                    content = ''
                    for chunk in resp.streaming_content:
                        if chunk:
                            content += chunk.decode('utf-8')
                    failed_instance = FailedImports(json_object="json.dumps(row, indent=4, sort_keys=True, default=str)", error_message=content)    
                    failed_imported_document = await sync_to_async(ImportedDocuments.objects.get)(pk=id)
                    failed_instance.imported_document_id = failed_imported_document
                    await sync_to_async(failed_instance.save)()
                except Exception as error:
                    print("An exception occurred, while saving failed schedule!!", error)
    
        count = count + 1

    failed_imports_obj = await sync_to_async(FailedImports.objects.filter)(imported_document_id=id)
    failed_imports = await sync_to_async(get_failed_imports_serialized_data)(failed_imports_obj)
    uploaded_obj = await sync_to_async(Contract.objects.filter)(uploaded=True, imported_document_id=id)
    uploaded = await sync_to_async(get_contract_serialized_data)(uploaded_obj)
    on_queue_obj = await sync_to_async(Contract.objects.filter)(uploaded=False, imported_document_id=id)
    on_queue = await sync_to_async(get_contract_serialized_data)(on_queue_obj)
    imported_document = await sync_to_async(ImportedDocuments.objects.get)(pk=id)
    imported_document.failed_count = len(failed_imports)
    imported_document.successful_count = len(uploaded)
    imported_document.on_queue_count = len(on_queue)
    await sync_to_async(imported_document.save)()


async def contract_row_upload(data):
    response = await recurring_contract.create_contract(
        data.get('contract_number'), 
        data.get('service_type'), 
        data.get('customer_account_name'), 
        data.get('meta_data')
        )
    return response

def get_contract_serialized_data(db_results):
    serializer = ContractSerializer(db_results, many=True)
    return serializer.data

@async_task(app, bind=True)
async def import_recurring_payment_request_rows(self: celery.Task, data, id):
    for row in data:
        try:
            instance = RecurringPaymentRequest(
                contract_number=row.get('contract_number'), 
                amount=row.get('amount'), 
                currency=row.get('currency'), 
                cause=row.get('cause'), 
                notification_url=row.get('notification_url'), 
                meta_data=json.dumps(row.get('meta_data')), 
                json_object=json.dumps(row), 
                uploaded=False
            )
            imported_document = await sync_to_async(ImportedDocuments.objects.get)(pk=id)
            instance.imported_document_id = imported_document
            await sync_to_async(instance.save)()
        except Exception as error:
            print("An exception occurred, while importing payment requests!!", error)
            try:
                instance = FailedImports(json_object=json.dumps(row, indent=4, sort_keys=True, default=str), error_message=error)     
                imported_document = await sync_to_async(ImportedDocuments.objects.get)(pk=id)
                instance.imported_document_id = imported_document
                await sync_to_async(instance.save)()
            except Exception as error:
                print("An exception occurred, while saving failed payment requests!!", error)
    obj = await sync_to_async(RecurringPaymentRequest.objects.filter)(uploaded=False, imported_document_id=id)
    dep= await sync_to_async(get_recurring_payment_request_serialized_data)(obj)
    count = 0
    for row in dep:
        meta_data = {}
        if row.get('meta_data') != "" and row.get("meta_data") != None:
            meta_data = json.loads(row.get('meta_data'))
        if count >= 0:
            resp = await recurring_payment_request_row_upload({"contract_number": row.get('contract_number'), "amount": row.get('amount'), "currency": row.get('currency'), "cause": row.get('cause'), "notification_url": row.get('notification_url'), "meta_data": meta_data})
            if resp.status_code == 200 or resp.status_code == 201:
                recurring_payment_request_object = await sync_to_async(get_object_or_404)(RecurringPaymentRequest, pk=row.get('uuid'))
                recurring_payment_request_object.uploaded = True
                await sync_to_async(recurring_payment_request_object.save)()
            else:
                try:
                    content = ''
                    for chunk in resp.streaming_content:
                        if chunk:
                            content += chunk.decode('utf-8')
                    failed_instance = FailedImports(json_object="json.dumps(row, indent=4, sort_keys=True, default=str)", error_message=content)    
                    failed_imported_document = await sync_to_async(ImportedDocuments.objects.get)(pk=id)
                    failed_instance.imported_document_id = failed_imported_document
                    await sync_to_async(failed_instance.save)()
                except Exception as error:
                    print("An exception occurred, while saving failed schedule!!", error)
            
        count = count + 1

    failed_imports_obj = await sync_to_async(FailedImports.objects.filter)(imported_document_id=id)
    failed_imports = await sync_to_async(get_failed_imports_serialized_data)(failed_imports_obj)
    uploaded_obj = await sync_to_async(RecurringPaymentRequest.objects.filter)(uploaded=True, imported_document_id=id)
    uploaded = await sync_to_async(get_recurring_payment_request_serialized_data)(uploaded_obj)
    on_queue_obj = await sync_to_async(RecurringPaymentRequest.objects.filter)(uploaded=False, imported_document_id=id)
    on_queue = await sync_to_async(get_recurring_payment_request_serialized_data)(on_queue_obj)
    imported_document = await sync_to_async(ImportedDocuments.objects.get)(pk=id)
    imported_document.failed_count = len(failed_imports)
    imported_document.successful_count = len(uploaded)
    imported_document.on_queue_count = len(on_queue)
    await sync_to_async(imported_document.save)()


async def recurring_payment_request_row_upload(data):
    response = await recurring_contract.request_payment(
        data.get('contract_number'), 
        data.get('amount'), 
        data.get('currency'), 
        data.get('cause'), 
        data.get('start_at'), 
        data.get('notification_url')
        )
    return response

def get_recurring_payment_request_serialized_data(db_results):
    serializer = RecurringPaymentRequestSerializer(db_results, many=True)
    return serializer.data

def get_failed_imports_serialized_data(db_results):
    serializer = FailedImportsSerializer(db_results, many=True)
    return serializer.data