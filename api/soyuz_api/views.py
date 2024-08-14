import asyncio
import datetime
import json
from datetime import date

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .mixins import PublicApiMixin, ApiErrorsMixin
from .models import ExpeditorCheckouts
from .utils import RemoteDbManager


class DownloadCheckouts(PublicApiMixin, ApiErrorsMixin, APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)

            cursor = connection.cursor()
            cursor.execute(f"""
                SELECT [CustomerId], [DockNo], [Status], [TimeStamp] FROM ExpeditorCheckouts
                WHERE CAST([TimeStamp] AS DATE) = cast(getDATE() as date) AND [ExpeditorId] = '{data.get("userToken")}'
                AND [CustomerId] = '{data.get("customerId")}';
            """)
            rows = cursor.fetchall()
            return JsonResponse({"checkouts": rows}, json_dumps_params={'ensure_ascii': False},
                                status=status.HTTP_200_OK)
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadCheckouts(PublicApiMixin, ApiErrorsMixin, APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            cursor = connection.cursor()
            for d in data:
                if d["Status"] != None and d["Status"] != 'null':
                    cursor.execute(f"""
                        MERGE INTO [ExpeditorCheckouts] AS target
                        USING (VALUES ('{d["ExpeditorId"]}', '{d["CustomerId"]}', '{d["Date"]}', '{d["Status"]}', '{d["DockNo"]}')) 
                        AS source ([ExpeditorId], [CustomerId], [TimeStamp], [Status], [DockNo])
                        ON target.ExpeditorId = source.ExpeditorId
                           AND target.CustomerId = source.CustomerId
                           AND target.TimeStamp = source.TimeStamp
                           AND target.DockNo = source.DockNo
                        WHEN MATCHED THEN
                          UPDATE SET
                            target.Status = source.Status,
                            target.TimeStamp = source.TimeStamp
                        WHEN NOT MATCHED THEN
                          INSERT ([ExpeditorId], [CustomerId], [TimeStamp], [ServerTimeStamp], [Status], [DockNo])
                          VALUES ('{d["ExpeditorId"]}', '{d["CustomerId"]}', '{d["Date"]}', GETDATE(), '{d["Status"]}', '{d["DockNo"]}');
                    """)
                    cursor.commit()
            # rows = cursor.fetchall()
            return JsonResponse({}, json_dumps_params={'ensure_ascii': False},
                                status=status.HTTP_200_OK)
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class TestView(PublicApiMixin, ApiErrorsMixin, APIView):
    def get(self, request, *args, **kwargs):
        try:
            return JsonResponse({"status": "OK"}, json_dumps_params={'ensure_ascii': False},
                                status=status.HTTP_200_OK)
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UploadLogs(PublicApiMixin, ApiErrorsMixin, APIView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            text = ''
            if len(data) > 0:
                text = f'<b>Экспедитор:</b> {data[0]["expeditorId"]}'
                for d in data:
                    text += f'''
                    
<b>Запрос:</b> {d["request"]}

<b>Дата и время:</b> {d["datetime"]}

<b>Код ответа:</b> {d["statusCode"]}           

<b>Тело ответа:</b> {d["responseBody"]}

<b>Тело запроса:</b> {d["body"]} 
                    '''
            print(text)
            return JsonResponse({}, json_dumps_params={'ensure_ascii': False},
                                status=status.HTTP_200_OK)
        except Exception as e:
            print(f"An error occurred: {e}")
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
