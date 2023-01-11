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
from .user import *
import logging
"""Login Type
normal
mobile
social
"""
logger = logging.getLogger(__name__)

# class TeamListAPIView(ListAPIView):
#     ##permission_classes = [AllowAny]
#     # pagination_class = CustomPagination

#     serializer_class = ListTeamSerializers
    
#     queryset = Team.objects.all()


#     def get(self, request, *args, **kwargs):
#         # if not request.user.is_manager:
#         #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User not allowed"},
#         #                     status=status.HTTP_400_BAD_REQUEST)
#         queryset = self.get_queryset()
        
            
#         serializer = self.get_serializer(queryset, many=True)
#         # page = self.paginate_queryset(serializer.data)

#         return self.get_paginated_response(serializer)


class TeamListAPIView(ListAPIView):
    #permission_classes = [AllowAny]

    serializer_class = ListTeamSerializers
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user.id
        return Team.objects.filter(created_by=user)
    
    def get(self, request, *args, **kwargs):
        print(request.user)
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "All teams list",
                              "result": serializer.data},
                        status=status.HTTP_200_OK,)

class DuplicatePlayerAPIView(CreateAPIView):
    #permission_classes = [AllowAny]
    serializer_class = DuplicatePlayerSerializers
   
    queryset= Team.objects.all()
    def post(self, request, *args, **kwargs):
        try:
            
            team1 = Team.objects.filter(id=request.data['team1']).first()
            team_list = Team.objects.all()
            response=[]
            for team in team_list:
                image = ''
                if team.team_image:
                    image=str(team.team_image.url)
                if any(x in team1.player.all() for x in team.player.all()):
                    response.append({
                        "id":team.id,
                        "team_name":team.team_name,
                        "team_image":image,
                        "is_duplicated":True
                    })
                else:
                    response.append({
                        "id":team.id,
                        "team_name":team.team_name,
                        "team_image":image,
                        "is_duplicated":False
                    })
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "duplicate player",
                              "result": response},
                        status=status.HTTP_200_OK,)




class GetTeamPlayerAPIView(GenericAPIView):
    #permission_classes = [AllowAny]

    serializer_class = ListTeamSerializers
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        match = Match.objects.filter(id=self.kwargs["pk"]).first()
        team_list = [match.team1.id,match.team2.id]
        return Team.objects.filter(id__in=team_list)
    
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "All teams list",
                              "result": serializer.data},
                        status=status.HTTP_200_OK,)
# class GetTeamPlayerAPIView(GenericAPIView):
#     #permission_classes = [AllowAny]
#     serializer_class = MatchDetailSerializers
   
#     def get(self, request, *args, **kwargs):
#         match = Match.objects.filter(id=self.kwargs["pk"]).first()
        
#         team_list = [match.team1,match.team2]
#         response=[]
#         for team in team_list:
#             image = ''
#             if team.team_image:
#                 image=str(team.team_image.url)
#             response.append({
#                         "id":team.id,
#                         "team_name":team.team_name,
#                         "caption":team.caption.id,
#                         "wicket_keeper":team.wicket_keeper.id,
#                         "team_image":image,
#                         "players":team.player.all().values("id","username","profile_image","player_type")
#                     })

        
       
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "duplicate player",
                              "result": response},
                        status=status.HTTP_200_OK,)



import requests
class livescoreAPIView(ListAPIView):
    #permission_classes = [AllowAny]

    serializer_class = ListTeamSerializers
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        user = self.request.user.id
        return Team.objects.filter(created_by=user)
    
    def get(self, request, *args, **kwargs):
        

        # url = "https://cricket-live-data.p.rapidapi.com/fixtures-by-date/2022-11-13"
        # match_id = 2661757
        try:
            url = "https://cricket-live-data.p.rapidapi.com/match/2647203"

            headers = {
                "X-RapidAPI-Key": "90dce879eamsh81141148518d1c5p121a97jsn940488c2c827",
                "X-RapidAPI-Host": "cricket-live-data.p.rapidapi.com"
            }

            response = requests.request("GET", url, headers=headers)

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        # print(json(response.json()))
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "All teams list",
                              "result": response.json()},
                        status=status.HTTP_200_OK,)


class TeamCreateAPIView(GenericAPIView):
    #permission_classes = [AllowAny]

    serializer_class = CreateTeamSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:

            team_name = request.data["team_name"]
            team_image = request.FILES.get("team_image")
            caption = User.objects.filter(id=request.data["caption"],is_delete__in=[False]).first()
            wicket_keeper = User.objects.filter(id=request.data["wicket_keeper"],is_delete__in=[False]).first()
            players_list = request.data["player"]
            # user_id_list = request.data["user"]
            players_list = json.loads(players_list)
            users = User.objects.filter(id__in=players_list,is_delete__in=[False])


            # if Team.objects.filter(team_name=team_name).exists():
            #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "team is already exists"}, status=status.HTTP_400_BAD_REQUEST)
            
            team = Team.objects.create(team_name=team_name,team_image=team_image,caption=caption,wicket_keeper=wicket_keeper,created_by=self.request.user)

            team.player.set(users)
            team.save()
            if team_image:
                t_img = str(team.team_image.url)
            else:
                t_img = ''
            # session = boto3.session.Session()
            
            # today = datetime.datetime.now()

            # today = today.strftime("%Y-%m-%d-%H-%M-%S")

            # client.put_object(Bucket='tourlife_test',
            #                   Key='User/user'+str(user.id)+str(today)+'.png',
            #                   Body= profile_image,
            #                   ACL='public-read-write',
            #                   ContentType='image/png',
            #                   )

            # url = client.generate_presigned_url(ClientMethod='get_object',
            #                                     Params={'Bucket': 'tourlife_test',
            #                                             'Key': 'User/user'+str(user.id)+str(today)+'.png'}, HttpMethod=None)

            # url=url.split('?')
            # url=url[0]
            # user.profile_image=url
            # user.save()



            response_data = {
                "id": team.id,
                "team_name":team.team_name,
                "team_image":t_img,
                "caption":team.caption.username,
                "caption_first_name":team.caption.first_name,
                "caption_last_name":team.caption.last_name,
                "wicket_keeper":team.wicket_keeper.username,
                "wicket_keeper_first_name":team.wicket_keeper.first_name,
                "wicket_keeper_last_name":team.wicket_keeper.last_name,
                
                "player":team.player.all().values_list('username', flat=True),
                
            }
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "New team added!!",
                              "result": response_data},
                        status=status.HTTP_200_OK)




class TeamUpdateAPIView(CreateAPIView):
    #permission_classes = [AllowAny]

    serializer_class = CreateTeamSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        # if not request.user.is_manager:
        #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User not allowed"},status=status.HTTP_400_BAD_REQUEST)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            team_name = request.data["team_name"]
            team_image = request.FILES.get("team_image")
            caption = get_user_by_id(request.data["caption"])
            # caption = User.objects.filter(id=request.data["caption"]).exclude(is_delete=True).first()
            wicket_keeper = get_user_by_id(request.data["wicket_keeper"])
            # wicket_keeper = User.objects.filter(id=request.data["wicket_keeper"]).exclude(is_delete=True).first()
            players_list = request.data["player"]
            # user_id_list = request.data["user"]
            players_list = json.loads(players_list)
            users = User.objects.filter(id__in=players_list,is_delete__in=[False])

            id = self.kwargs["pk"]

            if not Team.objects.filter(id=id):
                logger.error("Team is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Team is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            
            # if User.objects.filter(username=username).exists() | User.objects.filter(email=email).exists():
            #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "This email or username is already exists"},
            #                     status=status.HTTP_400_BAD_REQUEST)
            # print(profile_image)
            team = Team.objects.get(id=id)

            # session = boto3.session.Session()
            
            # today = datetime.datetime.now()

            # today = today.strftime("%Y-%m-%d-%H-%M-%S")

            
            # if not user.profile_image== None:
            
            #     key=user.profile_image.split('test/')
            #     client.delete_object(Bucket='tourlife_test',
            #     Key=key[1],
            #     )

            # if not profile_image== None:
                
            #     client.put_object(Bucket='tourlife_test',
            #                     Key='User/user'+str(user.id)+str(today)+'.png',
            #                     Body= profile_image,
            #                     ACL='public-read-write',
            #                     ContentType='image/png',
            #                     )

            #     url = client.generate_presigned_url(ClientMethod='get_object',
            #                                         Params={'Bucket': 'tourlife_test',
            #                                         'Key': 'User/user'+str(user.id)+str(today)+'.png'}, HttpMethod=None)

            #     url=url.split('?')
            #     url=url[0]
            #     user.profile_image = url 
            # team = Team.objects.create(team_name=team_name,team_image=team_image,caption=caption,wicket_keeper=wicket_keeper)
            


            team.team_name=team_name
            team.team_image=team_image
            if not caption == None:
                team.caption=caption
            else:
                logger.error("caption you selected is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "caption you selected is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not wicket_keeper == None:
                team.wicket_keeper=wicket_keeper
            else:
                logger.error("wicket keeper you selected is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "wicket keeper you selected is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            team.player.set(users)
            team.save()
            if team_image:
                t_img = str(team.team_image.url)
            else:
                t_img = ''
            response_data = {
                "id": team.id,
                "team_name":team.team_name,
                "team_image":t_img,
                "caption":team.caption.username,
                "caption_first_name":team.caption.first_name,
                "caption_last_name":team.caption.last_name,
                "wicket_keeper":team.wicket_keeper.username,
                "wicket_keeper_first_name":team.wicket_keeper.first_name,
                "wicket_keeper_last_name":team.wicket_keeper.last_name,
                
                "player":team.player.all().values_list('username', flat=True),
                
            }

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "Team updated",
                              "result": response_data},
                        status=status.HTTP_200_OK)