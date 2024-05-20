from __future__ import absolute_import, unicode_literals

import celery
from yayawallet_python_sdk.api import airtime
from asgiref.sync import async_to_sync
from asgiref.sync import sync_to_async
from .models import Scheduled
from yayawallet_python_sdk.api import scheduled
from python_server.celery import app
from .async_task import async_task
from .serializers import ScheduledSerializer
import json
from django.shortcuts import get_object_or_404

@async_task(app, bind=True)
async def import_scheduled_rows(self: celery.Task):
    obj = await sync_to_async(Scheduled.objects.filter)(uploaded=False)
    dep= await sync_to_async(get_serialized_data)(obj)
    count = 0
    for row in dep:
        meta_data = {}
        if row.get('meta_data') != "" and row.get("meta_data") != None:
            meta_data = json.loads(row.get('meta_data'))
        print({"account_number": row.get('account_number'), "amount": row.get('amount'), "reason": row.get('reason'), "recurring": row.get('recurring'), "start_at": row.get('start_at'), "meta_data": meta_data})
        if count >= 0:
            await row_upload({"account_number": row.get('account_number'), "amount": row.get('amount'), "reason": row.get('reason'), "recurring": row.get('recurring'), "start_at": row.get('start_at'), "meta_data": meta_data})
            scheduled_object = await sync_to_async(get_object_or_404)(Scheduled, pk=row.get('uuid'))
            scheduled_object.uploaded = True
            await sync_to_async(scheduled_object.save)()
        count = count + 1


async def row_upload(data):
    response = await scheduled.create(
        data.get('account_number'), 
        data.get('amount'), 
        data.get('reason'), 
        data.get('recurring'), 
        data.get('start_at'), 
        data.get('meta_data')
        )
    return response

def get_serialized_data(db_results):
    serializer = ScheduledSerializer(db_results, many=True)
    return serializer.data