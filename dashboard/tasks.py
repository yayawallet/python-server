from __future__ import absolute_import, unicode_literals

import celery
from yayawallet_python_sdk.api import airtime
from asgiref.sync import sync_to_async
from .models import Scheduled, Contract, FailedContract, RecurringPaymentRequest
from yayawallet_python_sdk.api import scheduled, recurring_contract
from python_server.celery import app
from .async_task import async_task
from .serializers.serializers import ScheduledSerializer, ContractSerializer, FailedContractSerializer, RecurringPaymentRequestSerializer
import json
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest

@async_task(app, bind=True)
async def import_scheduled_rows(self: celery.Task):
    obj = await sync_to_async(Scheduled.objects.filter)(uploaded=False)
    dep= await sync_to_async(get_scheduled_serialized_data)(obj)
    count = 0
    for row in dep:
        meta_data = {}
        if row.get('meta_data') != "" and row.get("meta_data") != None:
            meta_data = json.loads(row.get('meta_data'))
        if count >= 0:
            await scheduled_row_upload({"account_number": row.get('account_number'), "amount": row.get('amount'), "reason": row.get('reason'), "recurring": row.get('recurring'), "start_at": row.get('start_at'), "meta_data": meta_data})
            scheduled_object = await sync_to_async(get_object_or_404)(Scheduled, pk=row.get('uuid'))
            scheduled_object.uploaded = True
            await sync_to_async(scheduled_object.save)()
        count = count + 1


async def scheduled_row_upload(data):
    response = await scheduled.create(
        data.get('account_number'), 
        data.get('amount'), 
        data.get('reason'), 
        data.get('recurring'), 
        data.get('start_at'), 
        data.get('meta_data')
        )
    return response

def get_scheduled_serialized_data(db_results):
    serializer = ScheduledSerializer(db_results, many=True)
    return serializer.data

@async_task(app, bind=True)
async def import_contract_rows(self: celery.Task, data):
    for row in data:
        try:
            instance = Contract(contract_number=row.get('contract_number'), service_type=row.get('service_type'), customer_account_name=row.get('customer_account_name'), meta_data=json.dumps(row.get('meta_data')), json_object=json.dumps(row), uploaded=False)
            await sync_to_async(instance.save)()
        except:
            print("An exception occurred, while importing contract!!")
            try:
                instance = FailedContract(json_object=json.dumps(row))    
                await sync_to_async(instance.save)()
            except:
                print("An exception occurred, while importing failed contract!!")
    obj = await sync_to_async(Contract.objects.filter)(uploaded=False)
    dep= await sync_to_async(get_contract_serialized_data)(obj)
    count = 0
    for row in dep:
        meta_data = {}
        if row.get('meta_data') != "" and row.get("meta_data") != None:
            meta_data = json.loads(row.get('meta_data'))
        if count >= 0:
            await contract_row_upload({"contract_number": row.get('contract_number'), "service_type": row.get('service_type'), "customer_account_name": row.get('customer_account_name'), "meta_data": meta_data})
            contract_object = await sync_to_async(get_object_or_404)(Contract, pk=row.get('uuid'))
            contract_object.uploaded = True
            await sync_to_async(contract_object.save)()
        count = count + 1


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
async def import_recurring_payment_request_rows(self: celery.Task, request):
    uploaded_file = request.FILES['file']
    if not uploaded_file.name.endswith('.json'):
        return HttpResponseBadRequest("The uploaded file is not a JSON file.")
    instances = []
    json_data = uploaded_file.read().decode('utf-8')
    data = json.loads(json_data)
    for row in data:
        instance = RecurringPaymentRequest(contract_number=row.get('contract_number'), amount=row.get('amount'), currency=row.get('currency'), cause=row.get('cause'), notification_url=row.get('notification_url'), meta_data=json.dumps(row.get('meta_data')), json_object=json.dumps(row), uploaded=False)
        instances.append(instance)
    await sync_to_async(RecurringPaymentRequest.objects.bulk_create)(instances)
    obj = await sync_to_async(RecurringPaymentRequest.objects.filter)(uploaded=False)
    dep= await sync_to_async(get_recurring_payment_request_serialized_data)(obj)
    count = 0
    for row in dep:
        meta_data = {}
        if row.get('meta_data') != "" and row.get("meta_data") != None:
            meta_data = json.loads(row.get('meta_data'))
        if count >= 0:
            await recurring_payment_request_row_upload({"contract_number": row.get('contract_number'), "amount": row.get('amount'), "currency": row.get('currency'), "cause": row.get('cause'), "notification_url": row.get('notification_url'), "meta_data": meta_data})
            recurring_payment_request_object = await sync_to_async(get_object_or_404)(RecurringPaymentRequest, pk=row.get('uuid'))
            recurring_payment_request_object.uploaded = True
            await sync_to_async(recurring_payment_request_object.save)()
        count = count + 1


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