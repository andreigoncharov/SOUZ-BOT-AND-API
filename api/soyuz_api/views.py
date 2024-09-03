import asyncio
import datetime
import json
import traceback
from datetime import date

from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from aiogram import Bot

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
            print(data)
            if len(data) > 0:
                text = f'<b>Логи от экспедитора:</b> {data[0]["expeditorSurname"]} ({data[0]["expeditorId"]})'
                for d in data:
                    text += f'''
                    
<b>Запрос:</b> {d["request"]}

<b>Дата и время:</b> {d["datetime"]}

<b>Код ответа:</b> {d["statusCode"]}           

<b>Тело ответа:</b> {d["responseBody"]}

<b>Тело запроса:</b> {d["body"]}

--------- 
                    '''
            res_text = split_message(text)
            bot = Bot("7159327016:AAF4OFAMhiayZJLJw4ky2SI80vjehbMIi-Y")
            tel_id = 301735028
            tel_id2 = 420404892
            if len(res_text) == 1:
                asyncio.run(bot.send_message(tel_id, res_text[0], parse_mode='html'))
                asyncio.run(bot.send_message(tel_id2, res_text[0], parse_mode='html'))
            else:
                for t in res_text:
                    if t != res_text[len(res_text) - 1]:
                        asyncio.run(bot.send_message(tel_id, t, parse_mode='html'))
                        asyncio.run(bot.send_message(tel_id2, t, parse_mode='html'))
                    else:
                        asyncio.run(bot.send_message(tel_id, t, parse_mode='html'))
                        asyncio.run(bot.send_message(tel_id2, t, parse_mode='html'))
            if len(res_text) == 1:
                asyncio.run(bot.send_message(tel_id, res_text[0], parse_mode='html'))
                asyncio.run(bot.send_message(tel_id2, res_text[0], parse_mode='html'))
            else:
                for t in res_text:
                    if t != res_text[len(res_text) - 1]:
                        asyncio.run(bot.send_message(tel_id, t, parse_mode='html'))
                        asyncio.run(bot.send_message(tel_id2, t, parse_mode='html'))
                    else:
                        asyncio.run(bot.send_message(tel_id, t, parse_mode='html'))
                        asyncio.run(bot.send_message(tel_id2, t, parse_mode='html'))
            return JsonResponse({}, json_dumps_params={'ensure_ascii': False},
                                status=status.HTTP_200_OK)
        except Exception as e:
            print(f"An error occurred: {e}")
            tel_id = 420404892
            bot = Bot("7159327016:AAF4OFAMhiayZJLJw4ky2SI80vjehbMIi-Y")
            asyncio.run(bot.send_message(tel_id, traceback.format_exc(), parse_mode='html'))
            return Response({"error": "Internal Server Error"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



def split_message(text):
    def message_chunks(text):
        while len(text) > 4096:
            split_pos = text.rfind('\n', 0, 4096)
            if split_pos == -1:
                split_pos = 4096
            yield text[:split_pos]
            text = text[split_pos:]
        yield text

    return list(message_chunks(text))


class Logs(PublicApiMixin, ApiErrorsMixin, APIView):
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)
        print(data)
        return JsonResponse({}, json_dumps_params={'ensure_ascii': False},
                            status=status.HTTP_200_OK)