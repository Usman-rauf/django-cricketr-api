from django.shortcuts import render
from tempfile import tempdir
from .models import *
from .serializer import *
from rest_framework.generics import GenericAPIView, ListAPIView, CreateAPIView, UpdateAPIView, RetrieveAPIView, DestroyAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
# import boto3
import jwt
from django.conf import settings
from rest_framework.authentication import TokenAuthentication, get_authorization_header
import random
from django.conf import settings
from django.core.mail import send_mail
# from .pagination import CustomPagination
from rest_framework.pagination import PageNumberPagination
import json
from django.template.loader import get_template 
from django.template.loader import render_to_string
from rest_framework.renderers import JSONRenderer
from django.shortcuts import render
from django.http import HttpResponse
import pymongo
from dateutil.relativedelta import relativedelta
import logging
logger = logging.getLogger(__name__)

"""Login Type
normal
mobile
social
"""


def get_user_by_id(id):
    if not User.objects.filter(id=id,is_delete__in=[False]):
        return None
    return User.objects.filter(id=id,is_delete__in=[False]).first()

import pytz

utc=pytz.UTC

# Create your views here.
class LoginAPIView(GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = LoginUserSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        # email = serializer.validated_data['email']
        # password = serializer.validated_data['password']
        try:
            user=None
            login_type = request.POST.get("login_type")
            if login_type == 'normal':
                email = request.POST.get("email")
                # username = request.POST.get("username")
                password = request.POST.get("password")
                if email:
                    user = User.objects.filter(username=email).first()
                    if not user:
                        user = User.objects.filter(email=email).first()
                    if user:
                        if not user.password == password:
                            logger.error("Invalid email/username or password")
                            return Response(data={"status": status.HTTP_400_BAD_REQUEST, 'error': True, 'is_register': True, "message": "Invalid email/username or password"}, status=status.HTTP_400_BAD_REQUEST)
                        
            if login_type == 'mobile':
                mobile_no = request.POST.get("mobile_no")
                uuid = request.POST.get("uuid")
                user = User.objects.filter(mobile_no=mobile_no, uuid=uuid).first()
            if login_type == 'social':
                uuid = request.POST.get("uuid")
                user = User.objects.filter(uuid=uuid).first()


            if not user:
                logger.error("User not found, please sign up first..!")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, 'error': True, 'is_register': False, "message": "User not found, please sign up first..!"}, status=status.HTTP_400_BAD_REQUEST)
            
            if not user.is_delete == False:
                logger.error("Your account has been deactivated, Please contact us for account activation.")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, 'error': True, 'is_register': False, "message": "Your account has been deactivated, Please contact us for account activation."}, status=status.HTTP_400_BAD_REQUEST)
            
            # if user.is_delete == True:
            #     return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': "User not exists"}, status=status.HTTP_400_BAD_REQUEST)

            # ---------------------------------------------------------- check subscription -----------------------------------------------------------------
            pro_check = Subscription.objects.filter(user=user).last()
            if pro_check:
                if pro_check.end_time < utc.localize(datetime.today()):
                    user.is_pro=False
                    user.save()

            payload = {"username": user.username}
            device_token = request.POST.get("device_token")
            user.device_token=device_token
            user.save()
            jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "User Login Successfully.",
                              'is_register': True,
                            #   'credential_error':False,
                              "result": {'id': user.id,
                                        'username': user.username,
                                        'first_name': user.first_name,
                                        'last_name': user.last_name,
                                        "email" : user.email,
                                        "country" : user.country,
                                        "profile_image" : str(user.profile_image),
                                        # "cover_image": str(user.cover_image),
                                        "player_type" : user.player_type,
                                        "batsman_type" : user.batsman_type,
                                        "bowler_type" : user.bowler_type,
                                        "device_token":user.device_token,
                                        "is_pro":user.is_pro,
                                        "token": jwt_token,}},
                        status=status.HTTP_200_OK)


class UserCreateAPIView(GenericAPIView):
    permission_classes = [AllowAny]

    serializer_class = CreateUserSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            uuid = request.data["uuid"]

            jersey_no = request.data["jersey_no"]
            username = request.data["username"]+request.data["jersey_no"]
            password = request.data["password"]
            email = request.data["email"]
            profile_image_url = request.POST.get("profile_image_url")
            profile_image = request.FILES.get("profile_image")
            player_type = request.data["player_type"]
            batsman_type = request.data["batsman_type"]
            bowler_type = request.data["bowler_type"]
            country = request.data["country"]
            mobile_no = request.data["mobile_no"]
            device_token = request.POST.get("device_token")
            first_name = request.POST.get("first_name")
            last_name = request.POST.get("last_name")

            

            p_image=''
            # if profile_image:
            #     p_image=profile_image
            # if profile_image_url:
            #     p_image=profile_image_url
            # print(User.objects.filter(username=username,is_delete__in=[True]).exists())
            # try:
            # except Exception as e:
            #     print(str(e),'----------------')
            if User.objects.filter(username=username,is_delete__in=[False]):
                logger.error("This username is already exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "This username is already exists"}, status=status.HTTP_400_BAD_REQUEST)
            if not (email == "") | (email == None):
                logger.error("This email is already exists")
                if User.objects.filter(email=email,is_delete__in=[False]):
                    return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "This email is already exists"}, status=status.HTTP_400_BAD_REQUEST)
            # if User.objects.filter(uuid=uuid,is_delete__in=[False]):
            #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "This uuid is already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            
            
            response_data={}
            user = User.objects.create(uuid=uuid,
                                        username=username,
                                        first_name=first_name,
                                        last_name=last_name,
                                        jersey_no=jersey_no,
                                        password=password,
                                        email=email,
                                        mobile_no=mobile_no,
                                        profile_image = profile_image,
                                        profile_image_url=profile_image_url,
                                        cover_image=profile_image,
                                        player_type=player_type,
                                        batsman_type=batsman_type,
                                        bowler_type=bowler_type,
                                        country=country,
                                        is_delete=False,
                                        device_token=device_token)
            if profile_image:
                p_img = str(user.profile_image.url)
                user.profile_image_url = str(user.profile_image.url)
            else:
                user.profile_image_url = profile_image_url
                p_img = ''

            payload = {"username": user.username}
            device_token = request.POST.get("device_token")
            user.device_token=device_token
            user.save()
            user.cover_image = user.profile_image_url
            user.save()
            jwt_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
            response_data = {
            "id": user.id,
            "uuid": user.uuid,
            "username": user.username,
            "first_name":user.first_name,
            "last_name":user.last_name,
            "password": user.password,
            "email": user.email,
            "country": user.country,
            "profile_image": p_img,
            "cover_image": p_img,
            "profile_image_url":profile_image_url,
            "player_type": user.player_type,
            "batsman_type": user.batsman_type,
            "bowler_type": user.bowler_type,
            "is_delete":user.is_delete,
            "jersey_no":user.jersey_no,
            "device_token":user.device_token,
            "is_pro":user.is_pro,
            "token":jwt_token,
            
            }
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


        
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "Add new user",
                              "result": response_data},
                        status=status.HTTP_200_OK)



class UserUpdateAPIView(CreateAPIView):
    #permission_classes = [AllowAny]

    serializer_class = UpdateUserSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        # if not request.user.is_manager:
        #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User not allowed"},status=status.HTTP_400_BAD_REQUEST)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        # username = request.data["username"]
        country = request.POST.get("country")
        
        # profile_image = request.FILES.get("profile_image")
        player_type = request.data["player_type"]
        batsman_type = request.data["batsman_type"]
        bowler_type = request.data["bowler_type"]
        address = request.data["address"]
        first_name = request.POST.get("first_name")
        last_name = request.POST.get("last_name")
        # device_token = request.POST.get("device_token")
        id = self.kwargs["pk"]
        if not User.objects.filter(id=id,is_delete__in=[False]):
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User is not exists"},
                            status=status.HTTP_400_BAD_REQUEST)
        

        user = User.objects.get(id=id)

       
        if country:
            user.country = country
        if first_name:
            user.first_name=first_name
        if last_name:
            user.last_name=last_name
        # if profile_image:
        #     user.profile_image = profile_image
        if player_type:
            user.player_type = player_type
        if batsman_type:
            user.batsman_type = batsman_type
        if bowler_type:
            user.bowler_type = bowler_type
        if address:
            user.address = address
        # user.device_token=device_token
        user.save()
        

        image = ''
        if user.profile_image:
            image = str(user.profile_image.url)
        response_data = {
            "id": user.id,
            "username": user.username,
            "first_name":user.first_name,
            "last_name":user.last_name,
            "country": user.country,
            "profile_image": image,
            "player_type": user.player_type,
            "batsman_type": user.batsman_type,
            "bowler_type": user.bowler_type,
            "address": user.address,
            # "device_token":device_token,
            
        }
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "User updated",
                              "result": response_data},
                        status=status.HTTP_200_OK)


class ProfileUpdateAPIView(CreateAPIView):
    #permission_classes = [AllowAny]

    serializer_class = UpdateUserSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        # if not request.user.is_manager:
        #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User not allowed"},status=status.HTTP_400_BAD_REQUEST)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        # username = request.data["username"]
        try:
            type = request.POST.get("type")
            
            profile_image = request.FILES.get("profile_image")
            cover_image = request.FILES.get("cover_image")
            
            id = self.kwargs["pk"]
            if not User.objects.filter(id=id,is_delete__in=[False]):
                logger.error("User is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            

            user = User.objects.get(id=id)

            if type == 'profile':
                if profile_image:
                    user.profile_image = profile_image
            if type == 'cover':
                if cover_image:
                    user.cover_image = cover_image
            
            user.save()
            

            image = ''
            if user.profile_image:
                image = str(user.profile_image.url)
            cover = ''
            if user.cover_image:
                cover = str(user.cover_image.url)
            response_data = {
                "id": user.id,
                "username": user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                "profile_image": image,
                "cover_image": cover,
            
                
            }
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "Profile updated",
                              "result": response_data},
                        status=status.HTTP_200_OK)


class SearchUserAPIView(ListAPIView):
    #permission_classes = [AllowAny]

    serializer_class = AllUserSerializers
    def get_queryset(self,search_by):
        
        return User.objects.filter(username__contains=search_by,is_delete__in=[False])
    
    def get(self, request, *args, **kwargs):
        try:
            serch_by = self.kwargs["username"]
            queryset = self.get_queryset(serch_by)
            serializer = self.get_serializer(queryset, many=True)

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "Users",
                              "result": serializer.data},
                        status=status.HTTP_200_OK,)



class GetUserAPIView(ListAPIView):
    #permission_classes = [AllowAny]

    serializer_class = ListUserSerializers
    # renderer_classes = [JSONRenderer]

    def get(self, request, *args, **kwargs):
        # if not request.user.is_manager:
        #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User not allowed"},
        #                     status=status.HTTP_400_BAD_REQUEST)
        try:
            id = self.kwargs["pk"]
            if not User.objects.filter(id=id,is_delete__in=[False]):
                logger.error("User is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "user is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(id=id)
            
            # if Deliveries.objects.filter(batter=user,isWicketDelivery__in=[True]):
            #     total_out = len(Deliveries.objects.filter(batter=user,isWicketDelivery__in=[True]))


            # ---------------------------------------------------------- check subscription -----------------------------------------------------------------
            pro_check = Subscription.objects.filter(user=user).last()
            if pro_check:
                if pro_check.end_time < utc.localize(datetime.today()):
                    user.is_pro=False
                    user.save()

            img = str(user.profile_image.url) if user.profile_image else ''
            cover = str(user.cover_image.url) if user.cover_image else ''

            response={
            "uuid":user.uuid,
            "username":user.username,
            "first_name":user.first_name,
            "last_name":user.last_name,
            "jersey_no":user.jersey_no,
            "email":user.email,
            "mobile_no":user.mobile_no,
            "password":user.password,
            "address":user.address,
            "country":user.country,
            "device_token":user.device_token,
            "profile_image":img,
            "profile_image_url":user.profile_image_url,
            "cover_image":cover,
            "player_type":user.player_type,
            "batsman_type":user.batsman_type,
            "bowler_type":user.bowler_type,
            "total_innings":user.total_innings,
            "total_matches":user.total_matches,
            "total_run":user.total_run,
            "total_wicket":user.total_wicket,
            "total_ball":user.total_ball,
            "total_4":user.total_4,
            "total_6":user.total_6,
            "total_50":user.total_50,
            "total_100":user.total_100,
            "average":user.average,
            "is_pro":user.is_pro,
            "total_out":len(Deliveries.objects.filter(batter=user,isWicketDelivery__in=[True])),
        }
        # total_innings

        # total_matches
        
        # total_run
        # total_wicket
        # total_ball
        # total_4
        # total_6
        # total_50
        # total_100
        
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # queryset = self.get_queryset()
        # serializer = self.get_serializer(user)
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "user details",
                              "result": response},
                        status=status.HTTP_200_OK,)

class AllUserAPIView(ListAPIView):
    # permission_classes = [AllowAny]

    serializer_class = AllUserSerializers
    queryset = User.objects.filter(is_delete__in=[False])
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        try:
            final={}
            BATSMAN = []
            for user in serializer.data:
                if user['player_type'] == "BATSMAN":
                    BATSMAN.append(user)
            BOWLER = []
            for bowler in serializer.data:
                if bowler['player_type'] == "BOWLER":
                    BOWLER.append(bowler)
            ALL_ROUNDER = []
            for all_rounder in serializer.data:
                if all_rounder['player_type'] == "ALL-ROUNDER":
                    ALL_ROUNDER.append(all_rounder)
            
            WICKET_KEEPER = []
            for wicket_keeper in serializer.data:
                if wicket_keeper['player_type'] == "WICKET-KEEPER":
                    WICKET_KEEPER.append(wicket_keeper)
                    
            WICKET_KEEPER_L = []
            WICKET_KEEPER_R = []

            if len(WICKET_KEEPER) % 2 ==0 :
                l = int(len(WICKET_KEEPER)/2)

                WICKET_KEEPER_L.append(WICKET_KEEPER[:l])
                WICKET_KEEPER_R.append(WICKET_KEEPER[l:])
            else:
                l = int(len(WICKET_KEEPER)/2)
                WICKET_KEEPER_L.append(WICKET_KEEPER[:l])
                WICKET_KEEPER_R.append(WICKET_KEEPER[l:])

            for left in WICKET_KEEPER_L:
                for l in left:
                    BOWLER.append(l)
            for right in WICKET_KEEPER_R:
                for r in right:
                    BATSMAN.append(r)


            ALL_ROUNDER_L = []
            ALL_ROUNDER_R = []

            if len(ALL_ROUNDER) % 2 ==0 :
                l = int(len(ALL_ROUNDER)/2)

                ALL_ROUNDER_L.append(ALL_ROUNDER[:l])
                ALL_ROUNDER_R.append(ALL_ROUNDER[l:])
            else:
                l = int(len(ALL_ROUNDER)/2)
                ALL_ROUNDER_L.append(ALL_ROUNDER[:l])
                ALL_ROUNDER_R.append(ALL_ROUNDER[l:])

            for left in ALL_ROUNDER_L:
                for l in left:
                    BOWLER.append(l)
            for right in ALL_ROUNDER_R:
                for r in right:
                    BATSMAN.append(r)
            
            final['BATSMAN']=BATSMAN
            final['BOWLER']=BOWLER

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "user details",
                              "result": final},
                        status=status.HTTP_200_OK,)

class UserDeleteAPIView(GenericAPIView):
    #permission_classes = [AllowAny]

    serializer_class = CreateUserSerializers

    def post(self, request, *args, **kwargs):
        try:
            id = self.kwargs["pk"]
            type = request.data["type"]
            if not User.objects.filter(id=id,is_delete__in=[False]):
                logger.error("User is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)

            user = User.objects.get(id=id)
            if type == "disable":
                user.is_delete=True
                user.save()
            if type == "delete":
                user.username="Unknown"
                user.email=""
                user.mobile_no=""
                user.profile_image=""
                user.cover_image=""
                user.profile_image_url=""
                user.save()

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "User deleted"},
                        status=status.HTTP_200_OK)


class CheckEmailAPIView(GenericAPIView):
    permission_classes = [AllowAny]

    serializer_class = LoginUserSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        # if not request.user.is_manager:
        #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User not allowed"},status=status.HTTP_400_BAD_REQUEST)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            email = request.data["email"]
            
            # if User.objects.filter(email=email).exclude(is_delete=True).exists() | User.objects.filter(email=email).exclude(is_delete=True).exists():
            #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "This email is already exists"}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=email,is_delete__in=[False]):
                logger.error("This email is already exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "This email is already exists"}, status=status.HTTP_400_BAD_REQUEST)

            response_data = {
                
            }
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "Success",
                              "result": response_data},
                        status=status.HTTP_200_OK)


class CheckMobileAPIView(GenericAPIView):
    permission_classes = [AllowAny]

    serializer_class = LoginUserSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        # if not request.user.is_manager:
        #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User not allowed"},status=status.HTTP_400_BAD_REQUEST)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        try:
            mobile_no = request.data["mobile_no"]

            if User.objects.filter(mobile_no=mobile_no,is_delete__in=[False]):
                logger.error("This mobile_no is already exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "This mobile_no is already exists"}, status=status.HTTP_400_BAD_REQUEST)
            

            response_data = {
                
            }
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "Success",
                              "result": response_data},
                        status=status.HTTP_200_OK)



class BatsmanUserAPIView(ListAPIView):
    #permission_classes = [AllowAny]

    serializer_class = BatsmanUserSerializers
    # renderer_classes = [JSONRenderer]

    queryset = User.objects.filter(is_delete__in=[False])
    def get(self, request, *args, **kwargs):
        # serializer_class = BatsmanUserSerializers
        # renderer_classes = [JSONRenderer]

        # user = User.objects.all().exclude(is_delete=True)
        # if user.is_delete == True:
        #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "user is not exists"},
        #                     status=status.HTTP_400_BAD_REQUEST)


        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        try:
            batsman_user = []
            for user in serializer.data:
                if user['player_type'] == "BATSMAN":
                    batsman_user.append(user)
            # sort_user = sorted(batsman_user, key=lambda x: x.total_run)
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "user details",
                              "result": batsman_user},
                        status=status.HTTP_200_OK,)


class ForgotPasswordAPIView(GenericAPIView):
    #permission_classes = [AllowAny]
    serializer_class = ForgotpasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)

        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            email = request.data['email']
            if not User.objects.filter(email=email,is_delete__in=[False]):
                logger.error("email is not registered")
                return Response(data={"Status": status.HTTP_400_BAD_REQUEST, 'error': True, 'message': "email is not registered", }, status=status.HTTP_400_BAD_REQUEST)

            if User.objects.filter(email=email,is_delete__in=[False]):
                user = User.objects.filter(email=email).first()
                random_num = random.randint(1000, 9999)
                otp = random_num

                subject = 'send otp'
                message = 'your otp is {}'.format(otp)
                email_from = settings.EMAIL_HOST_USER
                recipient_list = [user.email]
                send_mail(subject, message, email_from, recipient_list)

                # User.objects.create(email=email, otp=otp)
                user = User.objects.filter(email=email,otp=otp,is_delete__in=[False])
                print(user)

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"Status": status.HTTP_200_OK, "error": False, 'message': 'We have sent you a otp to reset your password', "results": {"email": email, "otp": otp}}, status=status.HTTP_200_OK)


class TopUserListAPIView(ListAPIView):
    #permission_classes = [AllowAny]
    
    serializer_class = TopUserSerializers

    queryset = User.objects.filter(is_delete__in=[False])
    # print(queryset,"queryset")
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print(request.user.country)
        # print(User.objects.all().order_by('total_run').values(),"")
    
        try:
            response=[]
            if request.user.player_type == 'BATSMAN':
                user= User.objects.filter(player_type='BATSMAN',country=request.user.country,is_delete__in=[False]).order_by('total_run').order_by('-total_run')[:15]
                for i in user:
                    response.append({
                            "id":i.id,
                            "username":i.username,
                            'first_name': i.first_name,
                            'last_name': i.last_name,
                            "total_run":i.total_run,
                            "country":i.country,
                            # "player_type":i.player_type
                            # "profile_image":str(i.profile_image.url)
                            }
                    )
                # print(batsman_dic,"//////////////////")
            if request.user.player_type == 'BOWLER':
                user= User.objects.filter(player_type='BOWLER',country=request.user.country,is_delete__in=[False]).order_by('total_run').order_by('-total_run')[:15]
                for i in user:
                    response.append({
                        "id":i.id,
                        "username":i.username,
                        'first_name': i.first_name,
                        'last_name': i.last_name,
                        "total_wicket":i.total_wicket,
                        "country":i.country,

                    })
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
       
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "Top user List",
                              "result": response},
                        status=status.HTTP_200_OK,)



class worldTopUserListAPIView(ListAPIView):
    #permission_classes = [AllowAny]
    
    serializer_class = TopUserSerializers

    queryset = User.objects.filter(is_delete__in=[False])
    # print(queryset,"queryset")
    
    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        print(request.user.country)
        # print(User.objects.all().order_by('total_run').values(),"")
       
        try:
            response=[]
            if request.user.player_type == 'BATSMAN':
                user= User.objects.filter(player_type='BATSMAN',is_delete__in=[False]).order_by('total_run').order_by('-total_run')[:15]
                for i in user:
                    response.append({
                            "id":i.id,
                            "username":i.username,
                            'first_name': i.first_name,
                            'last_name': i.last_name,
                            "total_run":i.total_run,
                            "country":i.country,
                            # "player_type":i.player_type
                            # "profile_image":str(i.profile_image.url)
                            }
                    )
                # print(batsman_dic,"//////////////////")
            if request.user.player_type == 'BATSMAN':
                user= User.objects.filter(player_type='BOWLER',is_delete__in=[False]).order_by('total_run').order_by('-total_run')[:15]
                for i in user:
                    response.append({
                        "id":i.id,
                        "username":i.username,
                        'first_name': i.first_name,
                        'last_name': i.last_name,
                        "total_wicket":i.total_wicket,
                        "country":i.country,

                    })

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
       
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "Top user List",
                              "result": response},
                        status=status.HTTP_200_OK,)



class SubscriptionAPIView(GenericAPIView):
    #permission_classes = [AllowAny]

    serializer_class = SubscriptionSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user_id = request.data["user"]
            strip_user_id = request.data["strip_user_id"]
            payment_id = request.data["payment_id"]
            subscription_type = request.data["subscription_type"]
            duration = request.data["duration"]
            # start_time = datetime.now()

            user = User.objects.filter(id=user_id).first()
            
            # if subscription_type ==  "yearly":
            #     end_time = ''


            # if Team.objects.filter(team_name=team_name).exists():
            #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "team is already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            payment = Subscription.objects.create(

                    user=user,
                    strip_user_id=strip_user_id,
                    payment_id=payment_id,
                    subscription_type=subscription_type,
                    duration=duration,
                    
            )
            if payment.subscription_type ==  "monthly":
                payment.end_time = payment.start_time+ relativedelta(months=+int(payment.duration))
                payment.save()

            user.is_pro = True
            user.save()
            


            response_data = {
                "id":payment.id,
                "user":payment.user.username,
                "first_name":payment.user.first_name,
                "last_name":payment.user.last_name,
                "strip_user_id":payment.strip_user_id,
                "payment_id":payment.payment_id,
                "subscription_type":payment.subscription_type,
                "duration":payment.duration,
                "start_time":payment.start_time,
                "end_time":payment.end_time,
            }
            
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "New team added!!",
                              "result": response_data},
                        status=status.HTTP_200_OK)



