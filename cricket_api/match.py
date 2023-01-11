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
import logging
logger = logging.getLogger(__name__)


"""
extratypes
DB
WD
NB
"""

class CheckPlayerAPIView(GenericAPIView):
    #permission_classes = [AllowAny]

    serializer_class = CheckPlayerSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if not Team.objects.filter(id=request.data['team1']).first():
                logger.error("Team1 is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Team1 is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not Team.objects.filter(id=request.data['team2']).first():
                logger.error("Team2 is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Team2 is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
        
            # umpire need to be in both team and team_manager
            # toss winner must be in both team
            # openers must be in tose winner team
            team1 = Team.objects.filter(id=request.data['team1']).first()
            team2 = Team.objects.filter(id=request.data['team2']).first()
            
            if any(x in team1.player.all() for x in team2.player.all()):
                logger.error("Same player found in both team!!!")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Same player found in both team!!!"},
                                status=status.HTTP_400_BAD_REQUEST)
            
            response_data = {
                
            }
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "New match added!!",
                              "result": "success"},
                        status=status.HTTP_200_OK)



class MatchCreateAPIView(GenericAPIView):
    #permission_classes = [AllowAny]

    serializer_class = CreateMatchSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            if not Team.objects.filter(id=request.data['team1']).first():
                logger.error("Team1 is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Team1 is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not Team.objects.filter(id=request.data['team2']).first():
                logger.error("Team2 is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Team2 is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            if request.data['umpire']:
                if not User.objects.filter(id=request.data['umpire'],is_delete__in=[False]).first():
                    logger.error("umpire is not exists")
                    return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "umpire is not exists"},
                                    status=status.HTTP_400_BAD_REQUEST)
            if request.data['bowler']:
                if not User.objects.filter(id=request.data['bowler'],is_delete__in=[False]).first():
                    logger.error("bowler is not exists")
                    return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "bowler is not exists"},
                                    status=status.HTTP_400_BAD_REQUEST)
            # umpire need to be in both team and team_manager
            # toss winner must be in both team
            # openers must be in tose winner team
            team1 = Team.objects.filter(id=request.data['team1']).first()
            team2 = Team.objects.filter(id=request.data['team2']).first()
            
            # if any(x in team1.player.all() for x in team2.player.all()):
            #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Same player found in both team!!!"},
            #                     status=status.HTTP_400_BAD_REQUEST)
            date = request.data['date']
            time = request.data['time']
            venue = request.data['venue']
            umpire = User.objects.filter(id=request.data['umpire'],is_delete__in=[False]).first()
            is_toss = request.data['is_toss']
            team1_name = request.POST.get('team1_name')
            team2_name = request.POST.get('team2_name')
            now = datetime.now()
            if not date:
                date = now.strftime('%Y-%m-%d')
            if not time:
                time = now.strftime("%H:%M:%S")
            if team1_name:
                team1.team_name=team1_name
                team1.save()
            if team2_name:
                team2.team_name=team2_name
                team2.save()
            if is_toss == '1':
                tose_winner = Team.objects.filter(id=request.data['tose_winner']).first()
                toss_decision = request.data['toss_decision']
                opener_list = request.data['opener']
                opener_l = json.loads(opener_list)
                openers = User.objects.filter(id__in=opener_l,is_delete__in=[False])
                batting_team = Team.objects.filter(id=request.POST.get("batting_team")).first()
                bowing_team = Team.objects.filter(id=request.POST.get("bowing_team")).first()
                over = request.data['over']

                bowler = User.objects.filter(id=request.data['bowler'],is_delete__in=[False]).first()
            
                match = Match.objects.create(team1=team1,team2=team2,date=date,time=time,venue=venue,umpire=umpire,tose_winner=tose_winner,toss_decision=toss_decision,bowler=bowler,over=over,batting_team=batting_team,bowing_team=bowing_team,is_toss=is_toss)
            
                match.opener.set(openers)
                if match.date and match.time:
                    s_date = datetime.strptime(match.date, '%Y-%m-%d')
                    s_time = datetime.strptime(match.time, '%H:%M:%S')
                    match.schedule_datetime = datetime.combine(s_date, s_time.time())
                match.save()
                match.save()
                response_data = {
                    "id": match.id,
                    "team1":str(match.team1.id),
                    "team2":str(match.team2.id),
                    "date":match.date,
                    "time":match.time,
                    "venue":match.venue,
                    "umpire":match.umpire.id,
                    "tose_winner":match.tose_winner.id,
                    "toss_decision":match.toss_decision,
                    "bowler":str(match.bowler),
                    # "opener":match.opener.all().values_list('id', flat=True),
                    "over":match.over
                    
                }
            else:
                # s_date = datetime.strptime(datetime.date(), '%Y-%m-%d')
                # now = datetime.now()
                # s_date = now.strftime('%Y-%m-%d')
                # s_time = now.strftime("%H:%M:%S")
                # print(s_date,'===========================')
                # print(s_time,'===========================')
                match = Match.objects.create(team1=team1,team2=team2,date=date,time=time,venue=venue,umpire=umpire,is_toss=is_toss)
            
                response_data = {
                    "id": match.id,
                    "team1":str(match.team1.id),
                    "team2":str(match.team2.id),
                    "date":match.date,
                    "time":match.time,
                    "venue":match.venue,
                    "umpire":match.umpire.id,
                                    
                }

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "New match added!!",
                              "result": response_data},
                        status=status.HTTP_200_OK)

class MatchUpdateAPIView(CreateAPIView):
    permission_classes = [AllowAny]

    serializer_class = UpdateMatchSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        # if not request.user.is_manager:
        #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User not allowed"},status=status.HTTP_400_BAD_REQUEST)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            id = self.kwargs["pk"]

            if not Match.objects.filter(id=id).first():
                logger.error("Match is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Match is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)

            date = request.data["date"]
            time = request.data["time"]
            toss_decision = request.data["toss_decision"]
            tose_winner = Team.objects.filter(id=request.data["tose_winner"]).first()
            batting_team = Team.objects.filter(id=request.data["batting_team"]).first()
            bowing_team = Team.objects.filter(id=request.data["bowing_team"]).first()
            opener_list = request.data["opener"]
            opener_list = json.loads(opener_list)
            openers = User.objects.filter(id__in=opener_list,is_delete__in=[False])
            bowler = User.objects.filter(id=request.data["bowler"],is_delete__in=[False]).first()

            match = Match.objects.get(id=id)

            match.date = date
            match.time = time
            match.tose_winner = tose_winner
            match.toss_decision = toss_decision
            match.opener.set(openers)
            match.bowler = bowler
            match.batting_team= batting_team
            match.bowing_team = bowing_team
            match.save() 
            if match.date and match.time:
                s_date = datetime.strptime(match.date, '%Y-%m-%d')
                s_time = datetime.strptime(match.time, '%H:%M:%S')
                match.schedule_datetime = datetime.combine(s_date, s_time.time())
            match.save()
            
            response_data = {
                "id": match.id,
                "tose_winner": str(match.tose_winner),
                "batting_team":str(match.batting_team),
                "bowing_team":str(match.bowing_team),
                "opener":match.opener.all().values_list('username', flat=True),
                "bowler":str (match.bowler)
                
            }

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "match updated",
                              "result": response_data},
                        status=status.HTTP_200_OK)




class ChangeUmpireAPIView(CreateAPIView):
    # permission_classes = [AllowAny]

    serializer_class = ChangeUmpireSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        # if not request.user.is_manager:
        #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User not allowed"},status=status.HTTP_400_BAD_REQUEST)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            id = self.kwargs["pk"]

            if not Match.objects.filter(id=id).first():
                logger.error("Match is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Match is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)


            match = Match.objects.get(id=id)
            umpire = request.data['umpire']
            umpire_obj = User.objects.filter(id=umpire,is_delete__in=[False]).first()
            match.umpire = umpire_obj
            match.save() 
            
            
            response_data = {
                "id": match.id,
                "umpire_id": match.umpire.id,
                "umpire": match.umpire.username,
                "umpire_first_name": match.umpire.first_name,
                "umpire_last_name": match.umpire.last_name,
            
                
            }

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "umpire updated",
                              "result": response_data},
                        status=status.HTTP_200_OK)



from datetime import datetime
from datetime import date as dt
# class MatchListAPIView(ListAPIView):
#     #permission_classes = [AllowAny]

#     serializer_class = ListMatchSerializers
#     # queryset = Match.objects.all()
#     def get(self, request, *args, **kwargs):
#         queryset = Match.objects.all()
#         previous = []
#         live = []
#         upcomming = []
#         live_date = datetime.combine(datetime.today(), datetime.max.time())

#         for match in queryset:
#             # result=[]
        
        
#             team1_image = ''
#             if str(match.team1.team_image):
#                 team1_image = str(match.team1.team_image)
#             team2_image = ''
#             if str(match.team2.team_image):
#                 team2_image = str(match.team2.team_image)
            
#             bowl_team_image = ''
#             bat_team_image = ''
#             if match.bowing_team:
#                 if str(match.bowing_team.team_image):
#                     bowl_team_image = str(match.bowing_team.team_image)
#             if match.batting_team:
#                 if str(match.batting_team.team_image):
#                     bat_team_image = str(match.batting_team.team_image)
            
#             bowl_last_ball = 0
#             if Deliveries.objects.filter(match=match,BattingTeam=match.bowing_team,innings=match.innings).last():
#                 bowl_last_ball = Deliveries.objects.filter(match=match,BattingTeam=match.bowing_team,innings=match.innings).last().ballnumber
                
#             bat_last_ball = 0

#             if Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,innings=match.innings).last():
#                 bat_last_ball = Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,innings=match.innings).last().ballnumber
#             if match.is_toss == False:
#                 match_obj = {
#                 "id":match.id,
#                 "result":match.result,
#                 "team1_id":match.team1.id ,
#                 "team1_name":match.team1.team_name ,
#                 "team1_image":team1_image ,
#                 "team2_id":match.team2.id ,
#                 "team2_name":match.team2.team_name ,
#                 "team2_image":team2_image ,
#                 # "umpire_id":match.umpire.id ,
#                 # "umpire_name":match.umpire.username ,
#                 # "umpire_image":str(match.umpire.profile_image),
#                 "date":match.date ,
#                 "time":match.time ,
#                 "over":match.over ,
#                 "run":match.run,
#                 "wicket":match.wicket,
#                 "venue":match.venue ,
#                 # "tose_winner":match.tose_winner.team_name ,
#                 # "toss_decision":match.toss_decision ,
#                 # "opener":match.opener.all().values('id','username','profile_image'),
#                 # "batting_team":match.batting_team.team_name,
#                 # "bowler_id":match.bowler.id ,
#                 # "bowler_name":match.bowler.username ,
#                 # "bowler_image":str(match.bowler.profile_image),
#                 # "ball":match.ball,
#                 # "batting_team_players":{
#                 #     "id":match.batting_team.id ,
#                 #     "name":match.batting_team.team_name ,
#                 #     "image":bat_team_image ,
#                 #     "caption":match.batting_team.caption.username ,
#                 #     "run":get_run_of_team(match , match.batting_team),
#                 #     "wicket":Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,isWicketDelivery__in=[True]).count(),
#                 #     "over":int(int(Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,extras_run=0).count()) / 6),
#                 #     "ball_number":int(bat_last_ball),
#                 #     # "player_list":batting_team_player(match.batting_team.player.all(), match,match.innings),

#                 #     },
#                 # "bowing_team_players":{
#                 #     "id":match.bowing_team.id ,
#                 #     "name":match.bowing_team.team_name ,
#                 #     "image":bowl_team_image ,
#                 #     "caption":match.bowing_team.caption.username ,
#                 #     "run":get_run_of_team(match , match.bowing_team),
#                 #     "wicket":Deliveries.objects.filter(match=match,BattingTeam=match.bowing_team,isWicketDelivery__in=[True]).count(),
#                 #     "over":int(int(Deliveries.objects.filter(match=match,BattingTeam=match.bowing_team,extras_run=0).count()) / 6),
#                 #     "ball_number":int(bowl_last_ball),
#                 #     # "player_list":bowing_team_player(match.bowing_team.player.all(), match,match.innings),
#                 #     },
                
                
                
            
#                     }

#             if match.is_toss:
#                 match_obj = {
#                 "id":match.id,
#                 "result":match.result,
#                 "team1_id":match.team1.id ,
#                 "team1_name":match.team1.team_name ,
#                 "team1_image":team1_image ,
#                 "team2_id":match.team2.id ,
#                 "team2_name":match.team2.team_name ,
#                 "team2_image":team2_image ,
#                 "umpire_id":match.umpire.id ,
#                 "umpire_name":match.umpire.username ,
#                 "umpire_image":str(match.umpire.profile_image),
#                 "date":match.date ,
#                 "time":match.time ,
#                 "over":match.over ,
#                 "run":match.run,
#                 "wicket":match.wicket,
#                 "venue":match.venue ,
#                 "tose_winner":match.tose_winner.team_name ,
#                 "toss_decision":match.toss_decision ,
#                 "opener":match.opener.all().values('id','username','profile_image'),
#                 "batting_team":match.batting_team.team_name,
#                 "bowler_id":match.bowler.id ,
#                 "bowler_name":match.bowler.username ,
#                 "bowler_image":str(match.bowler.profile_image),
#                 "ball":match.ball,
#                 "batting_team_players":{
#                     "id":match.batting_team.id ,
#                     "name":match.batting_team.team_name ,
#                     "image":bat_team_image ,
#                     "caption":match.batting_team.caption.username ,
#                     "run":get_run_of_team(match , match.batting_team),
#                     "wicket":Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,isWicketDelivery__in=[True]).count(),
#                     "over":int(int(Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,extras_run=0).count()) / 6),
#                     "ball_number":int(bat_last_ball),
#                     "player_list":batting_team_player(match.batting_team.player.all(), match,match.innings),

#                     },
#                 "bowing_team_players":{
#                     "id":match.bowing_team.id ,
#                     "name":match.bowing_team.team_name ,
#                     "image":bowl_team_image ,
#                     "caption":match.bowing_team.caption.username ,
#                     "run":get_run_of_team(match , match.bowing_team),
#                     "wicket":Deliveries.objects.filter(match=match,BattingTeam=match.bowing_team,isWicketDelivery__in=[True]).count(),
#                     "over":int(int(Deliveries.objects.filter(match=match,BattingTeam=match.bowing_team,extras_run=0).count()) / 6),
#                     "ball_number":int(bowl_last_ball),
#                     "player_list":bowing_team_player(match.bowing_team.player.all(), match,match.innings),
#                     },
            
             
            
           
#                 }
#             # result.append(match_obj)
#             # match_obj = {
#             # "team1_id":match.team1.id ,
#             # "team1_name":match.team1.team_name ,
#             # "team1_image":match.team1.team_image ,
#             # "team2_id":match.team2.id ,
#             # "team2_name":match.team2.team_name ,
#             # "team2_image":match.team2.team_image ,
#             # "umpire_id":match.umpire.id ,
#             # "umpire_name":match.umpire.username ,
#             # "umpire_image":str(match.umpire.profile_image) ,
#             # "date":match.date ,
#             # "time":match.time ,
#             # "venue":match.venue ,
#             # "tose_winner":match.tose_winner.team_name ,
#             # "toss_decision":match.toss_decision ,
#             # "opener":match.opener.all().values('id','username','profile_image'),
#             # "bowler_id":match.bowler.id ,
#             # "bowler_name":match.bowler.username ,
#             # "bowler_image":str(match.bowler.profile_image) ,
#             # "over":match.over ,
#             #   }
#             date = datetime.combine(match.date,match.time)
            
#             # if (match.match_finish == True) or (date < datetime.now()):
#             #     previous.append(match_obj)
#             #     print('previous', match.id)
#             # if match.match_finish == False:
#             #     if date > datetime.now():
#             #         print('upcomming' ,match.id)
#             #         upcomming.append(match_obj)
#             #     else:
#             #         print('live', match.id)
#             #         live.append(match_obj)
#             #     # if datetime.now() < date:
#             #     #     # if datetime.now() <= date <= live_date:

#             if match.match_finish == True or date < datetime.now():
#                 previous.append(match_obj)
#                 print('previous')
#             if match.match_finish == False:
#                 if datetime.now() <= date <= live_date:
#                     print('live')
#                     live.append(match_obj)
#                 else:
#                     if  date > datetime.now():
#                         print('upcomming')
#                         upcomming.append(match_obj)

#         # serializer = self.get_serializer(queryset, many=True)
#         return Response(data={"status": status.HTTP_200_OK,
#                               "error": False,
#                               "message": "All teams list",
#                               "result": {
#                                 "previous":previous,
#                                 "live":live,
#                                 "upcomming":upcomming,
#                               }},
#                         status=status.HTTP_200_OK,)



import time
from django.db.models import Q
from django.db.models import DateTimeField, ExpressionWrapper, F

class Match_ListAPIView(ListAPIView):
    #permission_classes = [AllowAny]

    serializer_class = ListMatchSerializers
    # queryset = Match.objects.all()
    def get(self, request, *args, **kwargs):
        queryset = reversed(Match.objects.all())
        try:
            previous = []
            live = []
            upcomming = []
            live_date = datetime.combine(datetime.today(), datetime.max.time())
            D_obj = Deliveries.objects.all()
            for match in queryset:
                
                if match.is_toss  == True:
                    bowl_team_image = ''
                    bat_team_image = ''
                    # if match.bowing_team:
                    if str(match.bowing_team.team_image):
                        bowl_team_image = str(match.bowing_team.team_image)
                    # if match.batting_team:
                    if str(match.batting_team.team_image):
                        bat_team_image = str(match.batting_team.team_image)
                    
                    bowl_last_ball = 0
                    if D_obj.filter(match=match,BattingTeam=match.bowing_team,innings=match.innings).last():
                        bowl_last_ball = D_obj.filter(match=match,BattingTeam=match.bowing_team,innings=match.innings).last().ballnumber
                        
                    bat_last_ball = 0
                    if D_obj.filter(match=match,BattingTeam=match.batting_team,innings=match.innings).last():
                        bat_last_ball = D_obj.filter(match=match,BattingTeam=match.batting_team,innings=match.innings).last().ballnumber
                    match_obj = {
                        "match_id":match.id,
                        "umpire_id":match.umpire.id,
                        "result":match.result,
                        "total_over":match.over ,
                        "batting_team":match.batting_team.team_name,
                        "ball":match.ball,
                        "over":match.over,
                        "venue":match.venue,
                        "batting_team_players":{
                            "name":match.batting_team.team_name ,
                            "image":bat_team_image ,
                            "run":get_run_of_team(match , match.batting_team),
                            "wicket":D_obj.filter(match=match,BattingTeam=match.batting_team,isWicketDelivery__in=[True]).count(),
                            "over":int(int(D_obj.filter(match=match,BattingTeam=match.batting_team,extras_run=0).count()) / 6),
                            "ball_number":int(bat_last_ball),

                            },
                        "bowing_team_players":{
                            "name":match.bowing_team.team_name ,
                            "image":bowl_team_image ,
                            "run":get_run_of_team(match , match.bowing_team),
                            "wicket":D_obj.filter(match=match,BattingTeam=match.bowing_team,isWicketDelivery__in=[True]).count(),
                            "over":int(int(D_obj.filter(match=match,BattingTeam=match.bowing_team,extras_run=0).count()) / 6),
                            "ball_number":int(bowl_last_ball),
                            },
                        }
                if match.is_toss == False and match.match_finish == False:
                    team1_image = ''
                    if str(match.team1.team_image):
                        team1_image = str(match.team1.team_image)
                    team2_image = ''
                    if str(match.team2.team_image):
                        team2_image = str(match.team2.team_image)
                    match_obj = {
                        "match_id":match.id,
                        "umpire_id":match.umpire.id,
                        "result":match.result,
                        "team1_id":match.team1.id ,
                        "team1_name":match.team1.team_name ,
                        "team1_image":team1_image ,
                        "team2_id":match.team2.id ,
                        "team2_name":match.team2.team_name ,
                        "team2_image":team2_image ,
                        "over":match.over,
                        "venue":match.venue,
                        "date":match.date ,
                        "time":match.time ,
                        }
                
                date = datetime.combine(match.date,match.time)
                

                # match_t = Match.objects.filter(Q(match_finish__in=[True])|Q(schedule_datetime__lt=datetime.today()))
                # match_t = Match.objects.filter(Q(match_finish__in=[True])|Q(schedule_datetime__lt=date.today()))
                # print(len(match_t),'---------------------------------')
                # print(datetime.now(),'-=-=-=-=-=-=-=-=')
                # print(date,'-=-=-=-=-=-=-=-=')
                # print(live_date,'-=-=-=-=-=-=-=-=')

                # if match.match_finish == False and match.is_toss == True and  date <= datetime.now() <= live_date:

                if match.match_finish == True:
                    previous.append(match_obj)
                    print('previous')
                if match.match_finish == False and match.is_toss == True:

                    print('live')
                    live.append(match_obj)
                if  match.is_toss == False and date > datetime.now():
                    # if  date > datetime.now():
                    print('upcomming')
                    upcomming.append(match_obj)

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        # serializer = self.get_serializer(queryset, many=True)
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "All teams list",
                              "result": {
                                "previous":previous,
                                "live":live,
                                "upcomming":upcomming,
                              }},
                        status=status.HTTP_200_OK,)





from django.db.models import Sum
def batting_team_player(team, match,inning):
    team_players=[]
    
    for player in team:
        delevery = Deliveries.objects.filter(match=match,batter=player, innings=inning)
        # total run faced by betsman
        run = delevery.aggregate(Sum('batsman_run'))["batsman_run__sum"]
        if run == None:
            run = 0
        # total ball faced by betsman
        ball_faced = len(Deliveries.objects.filter(match=match,batter=player,extras_run=0, innings=inning))
        # total 4 hited by betsman
        total_4 = Deliveries.objects.filter(match=match,batter=player,batsman_run=4, innings=inning).count()
        # total 6 hited by betsman
        total_6 = Deliveries.objects.filter(match=match,batter=player,batsman_run=6, innings=inning).count()
        # out or not
        out = False
        out_by_username = ''
        out_by_first_name =''
        out_by_lastname =''
        kind = ''
        if Deliveries.objects.filter(match=match,player_out=player, innings=inning):
            out_by = Deliveries.objects.filter(match=match,player_out=player, innings=inning).first().bowler
            if out_by:
                out_by_username = out_by.username
                out_by_first_name = out_by.first_name
                out_by_lastname = out_by.last_name
            kind = Deliveries.objects.filter(match=match,player_out=player, innings=inning).first().kind
            out = True
        team_players.append({
            "player_id" : player.id,
            "player_name" : player.username,
            "player_first_name" : player.first_name,
            "player_last_name" : player.last_name,
            "player_image" : str(player.profile_image),
            "run":run,
            "ball_faced":ball_faced,
            "four":total_4,
            "six":total_6,
            "out":out,
            "out_by":out_by_username,
            "out_by_first_name":out_by_first_name,
            "out_by_last_name":out_by_lastname,
            "kind":kind,
        })
    return team_players
def current_batsman_stats(players, match):
    team_players=[]
    for player in players:
        delevery = Deliveries.objects.filter(match=match,batter=player)
        # total run faced by betsman
        run = delevery.aggregate(Sum('batsman_run'))["batsman_run__sum"]
        if run == None:
            run = 0
        # total ball faced by betsman
        ball_faced = len(Deliveries.objects.filter(match=match,batter=player,extras_run=0))
        # total 4 hited by betsman
        total_4 = len(Deliveries.objects.filter(match=match,batter=player,batsman_run=4))
        # total 6 hited by betsman
        total_6 = len(Deliveries.objects.filter(match=match,batter=player,batsman_run=6))
        # out or not
        out = False
        if Deliveries.objects.filter(match=match,player_out=player):
            out = True
        team_players.append({
            "id" : player.id,
            "username" : player.username,
            "first_name" : player.first_name,
            "last_name" : player.last_name,
            # "profile_image" : image,
            "run":run,
            "ball_faced":ball_faced,
            "four":total_4,
            "six":total_6,
            "out":out,
        })
    return team_players

def bowing_team_player(team, match,inning):
    team_players=[]
    for player in team:
        delevery = Deliveries.objects.filter(match=match,bowler=player,innings=inning)
        ball = len(Deliveries.objects.filter(match=match,bowler=player,extras_run=0,innings=inning))
        run = delevery.aggregate(Sum('batsman_run'))["batsman_run__sum"]
        if run == None:
            run = 0
        wicket = len(Deliveries.objects.filter(match=match,bowler=player,isWicketDelivery__in=[True],innings=inning))
        team_players.append({
            "player_id" : player.id,
            "player_name" : player.username,
            "player_first_name" : player.first_name,
            "player_last_name" : player.last_name,
            "player_image" : str(player.profile_image),
            "over": int(int(ball) / 6),
            "ball": ball,
            "maiden": 0,
            "run": run,
            "wicket": wicket,
        })
    return team_players


def get_run_of_team(match , team):
    run = Deliveries.objects.filter(match=match,BattingTeam=team).aggregate(Sum('total_run'))["total_run__sum"]
    if run == None:
        return 0
    return run

def get_run_of_team_inning(match , team,inning):
    run = Deliveries.objects.filter(match=match,BattingTeam=team,innings=inning).aggregate(Sum('total_run'))["total_run__sum"]
    if run == None:
        return 0
    return run

def get_last_over_log(match):
    out_player = ''
    out_player_first_name = ""
    out_player_last_name = ""
    last_over_log = []
    # last_over_number = int(int(Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,extras_run=0).count()) / 6)-1
    if Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,extras_run=0):
        last_over_number = Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,extras_run=0).last().overs
        last_over = Deliveries.objects.filter(match=match,innings=match.innings,overs=int(last_over_number)-1)
       
        for l in last_over:
            if l.player_out:
                out_player = l.player_out.username
                out_player_first_name = l.player_out.first_name
                out_player_last_name = l.player_out.last_name
            last_over_log.append({
                        "ballnumber":l.ballnumber,
                        "total_run":l.total_run,
                        "extras_run":l.extras_run,
                        "extra_type":l.extra_type,
                        "overs":l.overs,
                        "isWicketDelivery":l.isWicketDelivery,
                        "player_out":out_player,
                        "player_out_first_name":out_player_first_name,
                        "player_out_last_name":out_player_last_name,
                    })
    return last_over_log

# def get_current_over_log(match):
#     last_ball = Deliveries.objects.filter(match=match,bowler=match.bowler).last()
    
#     log_list = []
#     out_player = ''
#     current_over_ball = 0 
#     if last_ball:
#         over_ball_number = Deliveries.objects.filter(match=match,bowler=match.bowler)[0:last_ball.ballnumber]
#         current_over_ball = len(over_ball_number)
#         if over_ball_number == 6:
#             is_over = True
    
#         for l in over_ball_number:
#             if l.player_out:
#                 out_player = l.player_out.username
#             log_list.append({
#                         "ballnumber":l.ballnumber,
#                         "total_run":l.total_run,
#                         "extras_run":l.extras_run,
#                         "extra_type":l.extra_type,
#                         "overs":l.overs,
#                         "isWicketDelivery":l.isWicketDelivery,
#                         "player_out":out_player,
#                     })
                    
#     return log_list



def match_end(match):
    match_end = False
    team1_score = 0
    team2_score = 0

    last_ball = Deliveries.objects.filter(match=match,innings=match.innings).last()
    #if all out
    total_wicket = Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,isWicketDelivery__in=[True],innings=2).count()
    total_batting_players = match.batting_team.player.all().count()
    if total_wicket >= total_batting_players:
        match_end = True


    #if end overs 
    if last_ball:
        if int(last_ball.overs)+1 >= match.over:
            if last_ball.ballnumber == 6:
                if match.innings == 2:
                    match_end = True

    #if win by runs
    team1_run = Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,innings=2).aggregate(Sum('total_run'))["total_run__sum"]
    team2_run = Deliveries.objects.filter(match=match,BattingTeam=match.bowing_team,innings=2).aggregate(Sum('total_run'))["total_run__sum"]
    if team1_run:
        team1_score=team1_run
    if team2_run:
        team2_score=team2_run
    if team1_score > team2_score:
        match_end = True


    return match_end
class GetmatchAPIView(ListAPIView):
    #permission_classes = [AllowAny]

    serializer_class = ListMatchSerializers

    def get(self, request, *args, **kwargs):
        
        id = self.kwargs["pk"]
        if not Match.objects.filter(id=id):
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Match is not exists"},
                            status=status.HTTP_400_BAD_REQUEST)
        match = Match.objects.get(id=id)   
        match_obj = get_match_details(self, match)
        
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "user details",
                              "result": match_obj},
                        status=status.HTTP_200_OK,)

def get_match_details(self , match):
    is_umpire = False

    if match.umpire == self.request.user:
        is_umpire = True
    on_striker = ''
    off_striker = ''
    
    if Deliveries.objects.filter(match=match,innings=match.innings):
        on =  str(Deliveries.objects.filter(match=match,innings=match.innings).last().on_striker.id)
        off =  str(Deliveries.objects.filter(match=match,innings=match.innings).last().non_striker.id)
        l_ball = Deliveries.objects.filter(match=match,innings=match.innings).last()
        if l_ball.batsman_run == 1:
            on_striker = off
            off_striker = on
        elif l_ball.batsman_run == 3:
            on_striker = off
            off_striker = on
        else:
            on_striker = on
            off_striker = off
        
    delevery = Deliveries.objects.filter(match=match,bowler=match.bowler,innings=match.innings)
    # delevery = Deliveries.objects.filter(match=match,innings=match.innings)

    ball = Deliveries.objects.filter(match=match,bowler=match.bowler,extras_run=0,innings=match.innings).count()
    run = delevery.aggregate(Sum('batsman_run'))["batsman_run__sum"]
    wicket = Deliveries.objects.filter(match=match,bowler=match.bowler,isWicketDelivery__in=[True],innings=match.innings).count()
    last_ball = Deliveries.objects.filter(match=match,innings=match.innings).last()
    overs=0
    if last_ball:
        overs = last_ball.overs
    # is_over = False
    is_inning = False
    log_list = []
    out_player = ''
    out_player_first_name = ""
    out_player_last_name = ""
    current_over_ball = 0 

    

    if last_ball:
        current_over_ball = last_ball.ballnumber
        # if last_ball.ballnumber == 6:
        #     match.is_over = True
        #     match.save()
        # else:
        #     match.is_over = False
        #     match.save()
        if int(last_ball.overs)+1 >= match.over:
            if last_ball.ballnumber == 6:
                is_inning = True
                
    
        # if current_over_ball == 6:
        #     is_over = True
    
        for l in Deliveries.objects.filter(match=match,bowler=match.bowler,overs=last_ball.overs,innings=match.innings):
            if l.player_out:
                out_player = l.player_out.username
                out_player_first_name = l.player_out.first_name
                out_player_last_name = l.player_out.last_name
            log_list.append({
                        "ballnumber":l.ballnumber,
                        "total_run":l.total_run,
                        "extras_run":l.extras_run,
                        "extra_type":l.extra_type,
                        "overs":l.overs,
                        "isWicketDelivery":l.isWicketDelivery,
                        "player_out":out_player,
                        "player_out_first_name":out_player_first_name,
                        "player_out_last_name":out_player_last_name,
                    })
    bowler_obj = {
        "bowler_id":match.bowler.id ,
        "bowler_name":match.bowler.username ,
        "bowler_first_name":match.bowler.first_name ,
        "bowler_last_name":match.bowler.last_name ,
        "bowler_image":str(match.bowler.profile_image),
        "over": int(ball) / 6,
        "ball": ball,
        # "maiden": 0,
        "run": run,
        "wicket": wicket,
        "current_over":0,
        "ball_log":log_list
    }
    # print(match.batting_team.team_image)
    # print(match.batting_team.team_image)
    bowl_team_image = ''
    if match.bowing_team.team_image:
        bowl_team_image = str(match.bowing_team.team_image.url)
    bat_team_image = ''
    if match.batting_team.team_image:
        bat_team_image = str(match.batting_team.team_image.url)
    total_wicket = Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,isWicketDelivery__in=[True]).count()
    total_batting_player = match.batting_team.player.all().count()
    print(total_wicket)
    print(total_batting_player)
    if total_wicket >= total_batting_player-1:
        is_inning = True
        print('========================================')
    match_obj = {
    "is_umpire" :is_umpire,
    "is_inning":is_inning,
    "is_over":match.is_over,
    "match_end":match_end(match),
    "last_over":get_last_over_log(match),
    "batting_team":{
        "id":match.batting_team.id ,
        "name":match.batting_team.team_name ,
        "image":bat_team_image ,
        "caption":match.batting_team.caption.username ,
        "caption_first_name":match.batting_team.caption.first_name ,
        "caption_last_name":match.batting_team.caption.last_name ,
        "run":get_run_of_team(match , match.batting_team),
        "wicket":total_wicket,
        # "over":int(int(Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,extras_run=0,innings=match.innings).count()) / 6),
        "over":overs,
        "current_over_ball":current_over_ball,
        "player_list":batting_team_player(match.batting_team.player.all(), match,match.innings),

        },
    "bowing_team":{
        "id":match.bowing_team.id ,
        "name":match.bowing_team.team_name ,
        "image":bowl_team_image ,
        "caption":match.bowing_team.caption.username ,
        "caption_first_name":match.bowing_team.caption.first_name ,
        "caption_last_name":match.bowing_team.caption.last_name ,
        "run":get_run_of_team(match , match.bowing_team),
        "wicket":Deliveries.objects.filter(match=match,BattingTeam=match.bowing_team,isWicketDelivery__in=[True]).count(),
        # "over":int(int(Deliveries.objects.filter(match=match,BattingTeam=match.bowing_team,extras_run=0,innings=match.innings).count()) / 6),
        "over":overs,
        "current_over_ball":current_over_ball,
        "player_list":bowing_team_player(match.bowing_team.player.all(), match,match.innings),
        },
    
        "on_striker":on_striker,
        "off_striker":off_striker,
        "umpire_id":match.umpire.id ,
        "umpire_name":match.umpire.username ,
        "umpire_first_name":match.umpire.first_name ,
        "umpire_last_name":match.umpire.last_name ,
        "umpire_image":str(match.umpire.profile_image),
        "date":match.date ,
        "time":match.time ,
        "total_over":match.over ,
        "run":match.run,
        "wicket":match.wicket,
        "venue":match.venue ,
        "tose_winner":match.tose_winner.team_name ,
        "toss_decision":match.toss_decision ,
        "opener":current_batsman_stats(match.opener.all(), match),
        "batting_team_name":match.batting_team.team_name,
        "bowing_team_name":match.bowing_team.team_name,
        
        "bowler":bowler_obj,
        "ball":match.ball,
        
    
        }
    return match_obj


class DeleveriesAPIView(GenericAPIView):
    #permission_classes = [AllowAny]

    serializer_class = DeleveriesSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            match = Match.objects.filter(id=request.data['match']).first()
            # innings = request.data['innings']
            # overs = request.data['overs']
            # ballnumber = request.data['ballnumber']
            batter = User.objects.filter(id=request.data['batter'],is_delete__in=[False]).first()
            bowler = User.objects.filter(id=request.data['bowler'],is_delete__in=[False]).first()
            on_striker = User.objects.filter(id=request.data['on_striker'],is_delete__in=[False]).first()
            non_striker = User.objects.filter(id=request.data['non_striker'],is_delete__in=[False]).first()
            extra_type = request.data['extra_type']
            batsman_run = request.data['batsman_run']
            extras_run = request.data['extras_run']
            # total_run = request.data['total_run']
            # non_boundary = request.data['non_boundary']
            isWicketDelivery = request.data['isWicketDelivery']
        
            player_out = None
            fielders_involved = None
            if request.data['player_out']:
                player_out = User.objects.filter(id=request.data['player_out'],is_delete__in=[False]).first()
            kind = request.data['kind']
            if request.data['fielders_involved']:
                fielders_involved = User.objects.filter(id=request.data['fielders_involved'],is_delete__in=[False]).first()
            BattingTeam = Team.objects.filter(id=request.data['BattingTeam']).first()
            BowlingTeam = Team.objects.filter(id=request.data['BowlingTeam']).first()
            # SuperOver = request.data['SuperOver']


            ballnumber = 0
            overs = 0
            if Deliveries.objects.filter(match=match,innings=match.innings):
                check_inning = Deliveries.objects.filter(match=match,innings=match.innings,extras_run=0)
                ballnumber = Deliveries.objects.filter(match=match,innings=match.innings).last().ballnumber
                if ballnumber == 6:
                    ballnumber = 1
                    over = Deliveries.objects.filter(match=match,innings=match.innings).last().overs
                    overs = int(over) +1
                else:
                    overs = Deliveries.objects.filter(match=match,innings=match.innings).last().overs
                    if extra_type == "":
                        ballnumber += 1
                    if not extra_type == "":
                        ballnumber += 0
                    # if (int(extras_run) == 0):
                    #     ballnumber += 1
                    # elif int(extras_run) >0:
                    #     ballnumber += 0
            if not Deliveries.objects.filter(match=match,innings=match.innings):
                # if (int(extras_run) == 0):
                #     ballnumber += 1
                # elif int(extras_run) >0:
                #     ballnumber += 0
                if extra_type == "":
                    ballnumber += 1
                if not extra_type == "":
                    ballnumber += 0

            
            
        
            
            
                    
            # ()
            if not player_out == None:
                player_out =player_out
            else:
                player_out=None
            if not fielders_involved == None:
                fielders_involved =fielders_involved
            else:
                fielders_involved=None
            delivery = Deliveries.objects.create(
                    match=match,
                    innings=match.innings,
                    overs=overs,
                    ballnumber=ballnumber,
                    batter=batter,
                    bowler=bowler,
                    on_striker=on_striker,
                    non_striker=non_striker,
                    extra_type=extra_type,
                    batsman_run=batsman_run,
                    extras_run=extras_run,
                    total_run=int(batsman_run)+int(extras_run),
                    # non_boundary=non_boundary,
                    isWicketDelivery=isWicketDelivery,
                    player_out=player_out,
                    kind=kind,
                    fielders_involved=fielders_involved,
                    BattingTeam=BattingTeam,
                    BowlingTeam=BowlingTeam,
                    # SuperOver=SuperOver,
                    )
            
            if delivery.isWicketDelivery == '1':
                if delivery.kind =="Catch":
                    if delivery.fielders_involved:
                        msg = delivery.bowler.first_name+ " to " +delivery.on_striker.first_name+ " : Wicket!, caught-out by " +delivery.fielders_involved
                    else:
                        msg = delivery.bowler.first_name+ " to " +delivery.on_striker.first_name+ " : Wicket!, caught-out."
                    Commentary.objects.create(
                        match=match,
                        comment=msg,
                        type="WICKET",
                        over=overs,
                        stats="W"
                    )
                if delivery.kind =="Run":
                    if delivery.fielders_involved:
                        msg = delivery.bowler.first_name+ " to " +delivery.on_striker.first_name+ " : Wicket!, runout by " +delivery.fielders_involved
                    else:
                        msg = delivery.bowler.first_name+ " to " +delivery.on_striker.first_name+ " : Wicket!, runout."

                    Commentary.objects.create(
                        match=match,
                        comment=msg,
                        type="WICKET",
                        over=overs,
                        stats="W"
                    )
                if delivery.kind =="Stump":
                    if delivery.fielders_involved:
                        msg = delivery.bowler.first_name+ " to " +delivery.on_striker.first_name+ " : Wicket!, stumpout by " +delivery.fielders_involved
                    else:
                        msg = delivery.bowler.first_name+ " to " +delivery.on_striker.first_name+ " : Wicket!, stumpout."
                    Commentary.objects.create(
                        match=match,
                        comment=msg,
                        type="WICKET",
                        over=overs,
                        stats="W"
                    )
            else:
                if not delivery.extra_type == "":
                    msg = delivery.bowler.first_name+ " to " +delivery.on_striker.first_name+ " : " +delivery.extra_type+ delivery.extras_run+ " run"
                    Commentary.objects.create(
                        match=match,
                        comment=msg,
                        type="EXTRA",
                        over=overs,
                        stats= str(delivery.extra_type)+str(delivery.extras_run)
                    )
                else:
                    msg = delivery.bowler.first_name+ " to " +delivery.on_striker.first_name+ " : " +delivery.batsman_run+ " run"
                    Commentary.objects.create(
                        match=match,
                        comment=msg,
                        type="NORMAL",
                        over=overs,
                        stats=delivery.batsman_run
                    )


            last_ball = Deliveries.objects.filter(match=match,innings=match.innings).last()
            if last_ball:
                
                if last_ball.ballnumber == 6:
                    match.is_over = True
                    match.save()
                # else:
                #     match.is_over = False
                #     match.save()
            player_out = ''
            if player_out:
                player_out = player_out.username


            delevery = Deliveries.objects.filter(match=match,batter=delivery.batter)
            batter_run = delevery.aggregate(Sum('batsman_run'))["batsman_run__sum"]
            ball = Deliveries.objects.filter(match=match,bowler=delivery.batter,extras_run=0).count()
            total_4 = Deliveries.objects.filter(match=match,batter=delivery.batter,batsman_run=4).count()
            total_6 = Deliveries.objects.filter(match=match,batter=delivery.batter,batsman_run=6).count()
            total_50 =Deliveries.objects.filter(match=match,batter=delivery.batter,total_run__gt=50,total_run__lt=100).count()
            total_100 =Deliveries.objects.filter(match=match,batter=delivery.batter,total_run__gt=99,total_run__lt=199).count()
            # higest_score = delevery.aggregate(max(Sum('batsman_run')))
            # print(higest_score,'--------------------------------------------------------------')
            times_player_out = len(Deliveries.objects.filter(match=match,batter=delivery.batter,isWicketDelivery=True))
            average = int(batter_run)/int(times_player_out)

            total_match = len(Match.objects.all())
            User.objects.filter(username=batter).update(
                                                        total_run=batter_run,
                                                        total_ball=ball,
                                                        total_4=total_4,
                                                        total_6=total_6,
                                                        total_matches=total_match,
                                                        total_50=total_50,
                                                        total_100=total_100,
                                                        average=average
                                                        )
            wicket = Deliveries.objects.filter(match=match,bowler=bowler,isWicketDelivery__in=[True]).count()
            # ball = Deliveries.objects.filter(match=match,bowler=bowler,extras_run=0).count()
            # over = int(ball)/6
            User.objects.filter(username=bowler).update(total_wicket=wicket)

            


        

            response_data = get_match_details(self , match)
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "New match added!!",
                              "result": response_data},
                        status=status.HTTP_200_OK)






class UndoDeleveriesAPIView(GenericAPIView):
    #permission_classes = [AllowAny]

    serializer_class = UndoDeleveriesSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            match_id = request.POST.get("match")
            if Match.objects.filter(id=match_id).first():
                match = Match.objects.filter(id=match_id).first()
                
                Deliveries.objects.filter(match=match).last().delete()

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "last ball undo successfully!!",
                              "result": "success"},
                        status=status.HTTP_200_OK)



class UpdateBowlerAPIView(CreateAPIView):
    #permission_classes = [AllowAny]

    serializer_class = BowlerSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        # if not request.user.is_manager:
        #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User not allowed"},status=status.HTTP_400_BAD_REQUEST)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:

            match = request.data["match"]
            team = request.data["team"]
            bowler = User.objects.get(id=request.data['bowler'],is_delete__in=[False])
            if not Team.objects.filter(id=team):
                logger.error("Team is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Team is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not Match.objects.filter(id=match):
                logger.error("Match is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Match is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            
            team_obj = Team.objects.filter(id=team).first()
            
            
            if Match.objects.filter(id=match,team1=team_obj):
                match = Match.objects.filter(id=match,team1=team_obj).first()
            elif Match.objects.filter(id=match,team2=team_obj):
                match = Match.objects.filter(id=match,team2=team_obj).first()
            else:
                match=None
            match.bowler = bowler
            match.is_over = False
            match.save()


            response_data = {
            "bowler": str(match.bowler),
                
            }
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "bowler updated",
                              "result": response_data},
                        status=status.HTTP_200_OK)


class UpdateBatsmanAPIView(CreateAPIView):
    #permission_classes = [AllowAny]

    serializer_class = BatsmanSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        # if not request.user.is_manager:
        #     return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "User not allowed"},status=status.HTTP_400_BAD_REQUEST)
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)
        try:
            match = request.data["match"]
            team = request.data["team"]
            opener_list = request.data["opener"]
            opener_list = json.loads(opener_list)
            opener = User.objects.filter(id__in=opener_list,is_delete__in=[False])
            if not Team.objects.filter(id=team):
                logger.error("Team is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Team is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            if not Match.objects.filter(id=match):
                logger.error("Match is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Match is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            
            team_obj = Team.objects.filter(id=team).first()
            
            
            if Match.objects.filter(id=match,team1=team_obj):
                match = Match.objects.filter(id=match,team1=team_obj).first()
            elif Match.objects.filter(id=match,team2=team_obj):
                match = Match.objects.filter(id=match,team2=team_obj).first()
            else:
                match=None
            match.opener.set(opener)
            match.save()
            

            response_data = {
            "opener":match.opener.all().values(),
                
            }

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "Team updated",
                              "result": response_data},
                        status=status.HTTP_200_OK)

class UpdateInningAPIView(CreateAPIView):
    #permission_classes = [AllowAny]

    serializer_class = ChangeInningSerializers

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.POST)
        
        if not serializer.is_valid():
            logger.error(serializer.errors)
            return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": serializer.errors}, status=status.HTTP_400_BAD_REQUEST)

        
        try:
            if not User.objects.filter(id=request.data['bowler'],is_delete__in=[False]).first():
                logger.error("bowler is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "bowler is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
            
            match_id = request.POST.get("match")
            match = Match.objects.filter(id=match_id).first()

            print(match,'---------------------')
            inning = request.data["inning"]
            opener_list = request.data['opener']
            opener_l = json.loads(opener_list)
            openers = User.objects.filter(id__in=opener_l,is_delete__in=[False])
            batting_team = Team.objects.filter(id=request.POST.get("batting_team")).first()
            bowing_team = Team.objects.filter(id=request.POST.get("bowing_team")).first()
            bowler = User.objects.filter(id=request.data['bowler'],is_delete__in=[False]).first()
            match.is_over = False
            match.innings=inning
            match.bowler=bowler
            match.batting_team=batting_team
            match.bowing_team=bowing_team
            match.opener.set(openers)
            match.save()

            response_data = {
                "id": match.id,
                "team1":str(match.team1.id),
                "team2":str(match.team2.id),
                "date":match.date,
                "time":match.time,
                "venue":match.venue,
                "umpire":match.umpire.id,
                "tose_winner":match.tose_winner.id,
                "toss_decision":match.toss_decision,
                "bowler":str(match.bowler),
                # "opener":match.opener.all().values_list('id', flat=True),
                "over":match.over
                
            }

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "Team updated",
                              "result": response_data},
                        status=status.HTTP_200_OK)



def get_inning_data(match,inning):
    last_ball = Deliveries.objects.filter(match=match,bowler=match.bowler,innings = inning).last()
   
    current_over_ball = 0 
    if last_ball:
        over_ball_number = Deliveries.objects.filter(match=match,bowler=match.bowler,overs=last_ball.overs,innings=match.innings)[0:last_ball.ballnumber]
        current_over_ball = len(over_ball_number)
       
    bowl_team_image = ''
    if str(match.batting_team.team_image):
        bowl_team_image = str(match.batting_team.team_image)
    

    print(match.batting_team,'-------------')
    match_obj = {
    
    "batting_team":{
        "name":match.batting_team.team_name ,
        "image":bowl_team_image ,
        "run":get_run_of_team(match , match.batting_team),
        "wicket":len(Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,isWicketDelivery__in=[True],innings = inning)),
        "current_over":int(len(Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,extras_run=0,innings = inning)) / 6),
        "current_over_ball":current_over_ball,
        "player_list":batting_team_player(match.batting_team.player.all(), match,inning),

        },
    "bowing_team":{
        "player_list":bowing_team_player(match.bowing_team.player.all(), match,inning),
        },
        # "total_over":match.over ,
        }

    bat_team_image = ''
    if str(match.bowing_team.team_image):
        bat_team_image = str(match.bowing_team.team_image)
    
    match_obj2 = {
                "batting_team":{
                    "id":match.bowing_team.id ,
                    "name":match.bowing_team.team_name ,
                    "image":bat_team_image ,
                    "caption":match.bowing_team.caption.username ,
                    "caption_first_name":match.bowing_team.caption.first_name ,
                    "caption_last_name":match.bowing_team.caption.last_name ,
                    "run":0,
                    "wicket":0,
                    "current_over":0,
                    "current_over_ball":0,
                    "player_list":bowing_team_player(match.bowing_team.player.all(), match,inning),

                    },
                "bowing_team":{
                    "player_list":batting_team_player(match.batting_team.player.all(), match,inning),
                    },
                    # "total_over":match.over ,
                    }
    return [match_obj, match_obj2]

class GetscorecardAPIView(ListAPIView):
    #permission_classes = [AllowAny]

    serializer_class = ListMatchSerializers

    def get(self, request, *args, **kwargs):
        try:
            id = self.kwargs["pk"]
            if not Match.objects.filter(id=id):
                logger.error("Match is not exists")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Match is not exists"},
                                status=status.HTTP_400_BAD_REQUEST)

            match_inning1 = Match.objects.filter(id=id).first()      
            match_inning2 = Match.objects.filter(id=id,innings=2).first() 

            inning1 = {}
            inning2 = {}
            if match_inning1:
                inning1 = get_inning_data(match_inning1,1)[0]
            if match_inning2:
                inning2 = get_inning_data(match_inning2,2)[0]
            else:
                inning2 = get_inning_data(match_inning1,2)[1]
                
            on_striker = ''
            off_striker = ''
            innings = {
                "current_inning":"inning"+str(Match.objects.filter(id=id).first().innings),
                "match_result":match_inning1.result,
                "inning1":inning1,
                "inning2":inning2,
                }
            # result.append(match_obj)
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "user details",
                              "result": innings},
                        status=status.HTTP_200_OK,)


def team_detail(team):
    image = ""
    if team.team_image:
        image = str(team.team_image.url)
    return{
        "id": team.id,
        "team_name":team.team_name,
        "team_image":image,
        "best_score":team.best_score,
        "win_count":team.win_count,
        "lose_count":team.lose_count,
        "total_match":team.total_match,
        "caption":team.caption.id,
        "wicket_keeper":team.wicket_keeper.id,
        "player":team.player.all().values('id','username','profile_image','player_type'),
        "created_by":team.created_by.username,
        "created_by_first_name":team.created_by.first_name,
        "created_by_last_name":team.created_by.last_name,
        }
    

class dynamicTeamAPIView(GenericAPIView):
    #permission_classes = [AllowAny]
    
    serializer_class = DynamicTeamSerializers

    
    def post(self, request, *args, **kwargs):
        try:
            user_list =request.data["user"]
            user_list = json.loads(user_list)
            if len(user_list) < 4:
                logger.error("Please select at least 4 players!!!")
                return Response(data={"status": status.HTTP_400_BAD_REQUEST, "error": True, "message": "Please select at least 4 players!!!"},
                                status=status.HTTP_400_BAD_REQUEST)
            users = User.objects.filter(id__in=user_list,is_delete__in=[False])
            print(users,"????????????")
            users_len = len(users)
            team = users_len / 2
            team = {}
            team1 = []
            team2 = []

            if len(users) % 2 ==0 :
                l = int(len(users)/2)

                team1 = users[:l]
                # Team.objects.create(player=set(users[:l]))

                team2=users[l:]
            else:
                l = int(len(users)/2)
                team1=users[:l]
                team2=users[l:]

            

            team["team1"]= team1
            team["team2"] =team2
            
            team1_obj = Team.objects.create(
            team_name="team1",
            team_image="",
            best_score=0,
            win_count=0,
            lose_count=0,
            total_match=0,
            caption=team1[0],
            wicket_keeper=team1[1],
            created_by=team1[1],
            )
            team1_obj.player.set(team1)
            team1_obj.save()

            team2_obj = Team.objects.create(
            team_name="team2",
            team_image="",
            best_score=0,
            win_count=0,
            lose_count=0,
            total_match=0,
            caption=team2[0],
            wicket_keeper=team2[1],
            created_by=team2[1],
            )
            team2_obj.player.set(team2)
            team2_obj.save()


            response = {
                "team1":team_detail(team1_obj),
                "team2":team_detail(team2_obj),
            }

        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

      
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "team list",
                              "result": response},
                        status=status.HTTP_200_OK,)


class EndMatchAPIView(GenericAPIView):
    #permission_classes = [AllowAny]
    
    serializer_class = MatchDetailSerializers

    
    def post(self, request, *args, **kwargs):
        try:
            match =Match.objects.filter(id=request.data["match"]).first()
            if match:
                team1_score = 0
                team2_score = 0
                team1_run = Deliveries.objects.filter(match=match,BattingTeam=match.team1).aggregate(Sum('total_run'))["total_run__sum"]
                team2_run = Deliveries.objects.filter(match=match,BattingTeam=match.team2).aggregate(Sum('total_run'))["total_run__sum"]
                if team1_run:
                    team1_score=team1_run
                if team2_run:
                    team2_score=team2_run
                total_wicket = Deliveries.objects.filter(match=match,BattingTeam=match.batting_team,isWicketDelivery__in=[True],innings=2).count()
                total_batting_players = match.batting_team.player.all().count()
                if team1_score > team2_score:
                    wnning_team = match.batting_team
                    match.winner = wnning_team
                    match.match_finish = True
                    match.result = wnning_team.team_name+" won by "+str((int(total_batting_players)-int(total_wicket)))+" wicket"
                    match.save()
                    # print(wnning_team.team_name+" won by "+str((int(total_batting_players)-int(total_wicket)))+" wicket")
                if team1_score < team2_score:
                    wnning_team = match.bowing_team
                    match.winner = wnning_team
                    match.match_finish = True
                    match.result = wnning_team.team_name+" won by "+str((int(team2_score)-int(team1_score)))+" run"
                    match.save()
                    # print(wnning_team.team_name+" won by "+str((int(team2_score)-int(team1_score)))+" run")
            response = {
                "wnning_team": match.winner.team_name,
                "result":match.result,
            }
        except Exception as e:
            logger.error(str(e))
            return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

      
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "Match end!!!",
                              "result": response},
                        status=status.HTTP_200_OK,)



class CommentaryAPIView(ListAPIView):
    #permission_classes = [AllowAny]

    serializer_class = CommentarySerializers
    def get_queryset(self):
        
        id = self.kwargs["pk"]
        match = Match.objects.filter(id=id).first()
        return Commentary.objects.filter(match=match)
    
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
                              "message": "All match commentary",
                              "result": serializer.data},
                        status=status.HTTP_200_OK,)



