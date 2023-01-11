# from django.test import TestCase


# from django.shortcuts import render
# from tempfile import tempdir
# from .models import *
# from .serializer import *
# from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.permissions import AllowAny
# # import boto3
# import jwt
# from django.conf import settings
# from rest_framework.authentication import TokenAuthentication, get_authorization_header
# import random
# from django.conf import settings
# from django.core.mail import send_mail
# # from .pagination import CustomPagination
# from rest_framework.pagination import PageNumberPagination
# import json
# from django.template.loader import get_template 
# from django.template.loader import render_to_string
# from rest_framework.renderers import JSONRenderer
# from django.shortcuts import render
# from django.http import HttpResponse
# from django.db.models import Sum
# # Create your tests here.


# class ChatListAPIView(ListAPIView):
#     #permission_classes = [AllowAny]

#     serializer_class = ListchatSerializers
#     def get_queryset(self):
#         user_id = self.kwargs["pk"]
#         login_id = self.request.user.id
#         user_obj = User.objects.get(id = user_id,is_delete__in=[False])
#         # users = User.objects.exclude(id = login_id)
        
#         if login_id > user_obj.id:
#             thread_name = f'chat_{login_id}-{user_obj.id}'
#         else:
#             thread_name = f'chat_{user_obj.id}-{login_id}'
#         message_objs = ChatModel.objects.filter(thread_name=thread_name)
#         # user = self.request.user.id
#         return ChatModel.objects.filter(thread_name=thread_name), user_obj
    
#     def get(self, request, *args, **kwargs):
#         print(request.user)
#         queryset = self.get_queryset()[0]
#         usr = self.get_queryset()[1]
#         usr_obj={
#             "user_id":usr.id,
#             "user_username":usr.username,
#             "user_profile_image":usr.profile_image.url,
#         }
#         print(usr.username,'-=-=-=-=-=-=-=-=-=-=-=')
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(data={"status": status.HTTP_200_OK,
#                               "error": False,
#                               "message": "All teams list",
#                               "user": usr_obj,
#                               "count":len(serializer.data),
#                               "result": serializer.data,
#                               },
#                         status=status.HTTP_200_OK,)