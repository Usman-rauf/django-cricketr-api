from django.test import TestCase


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
from django.db.models import Sum
# Create your tests here.
from pymongo import MongoClient
import pymongo



class PreMatchesListAPIView(ListAPIView):
    #permission_classes = [AllowAny]

    serializer_class = ListMatchSerializers2
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        # user = self.request.user.id
        # match.match_finish == True
        return Match.objects.filter(match_finish__in=[True])
    
    def get(self, request, *args, **kwargs):
        print(request.user)
        # try:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # except Exception as e:
        #     logger.error(str(e))
        #     return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "All teams list",
                              "result": serializer.data},
                        status=status.HTTP_200_OK,)


class LiveMatchesListAPIView(ListAPIView):
    #permission_classes = [AllowAny]

    serializer_class = ListMatchSerializers2
    def get_queryset(self):
        """
        This view should return a list of all the purchases
        for the currently authenticated user.
        """
        # user = self.request.user.id
        # match.match_finish == True
        return Match.objects.filter(match_finish__in=[False],is_toss__in=[True])
    
    def get(self, request, *args, **kwargs):
        print(request.user)
        # try:
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)

        # except Exception as e:
        #     logger.error(str(e))
        #     return Response(data={'status': status.HTTP_400_BAD_REQUEST, 'error': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "All teams list",
                              "result": serializer.data},
                        status=status.HTTP_200_OK,)






myclient = MongoClient("mongodb+srv://manthan:manthan_1234@cluster0.q1fx6jn.mongodb.net/?retryWrites=true&w=majority")
mydb = myclient["cricket_db"]


# import os
# from dotenv import load_dotenv

# load_dotenv()

# myclient = MongoClient(os.getenv('DATABASE_HOST'))
# mydb = myclient[os.getenv('DATABASE_NAME')]


def get_run_of_team(match, team):
    cricket_api_deliveries = mydb["cricket_api_deliveries"]
    batting_team_name = ''
    batting_team_image = ''
    run = 0
    wicket = 0
    over = 0
    ball_number=0
    
    batting_team_name = team["team_name"]
    batting_team_image = team["team_image"]
    a = cricket_api_deliveries.aggregate([
                            {
                                '$match': { 'match_id': match["id"], 'BattingTeam_id': team['id'] },
                                # '$team': { 'BattingTeam_id': team },
                            },
                            {
                                '$group': { '_id': "$match_id", 'totalRun': { '$sum': "$total_run" } }
                            }
                        ])
    for i in a:
        run = i["totalRun"]
    
    wicket = cricket_api_deliveries.find({ 'match_id': match["id"], 'BattingTeam_id': team["id"] ,"isWicketDelivery" :True}).count()
    score = cricket_api_deliveries.find({ 'match_id': match["id"], 'BattingTeam_id': team["id"] ,'extra_type':''}).sort([('id', -1)]).limit(1)
    for i in score:
        over = i["overs"]
        ball_number = i["ballnumber"]
    
    return {"batting_team_name":batting_team_name,"batting_team_image":batting_team_image,"run":run,"wicket":wicket,"over":over,"ball_number":ball_number}

def get_team_name(team_id):
    mycol = mydb["cricket_api_team"]
    
    for x in mycol.find({ "id": team_id}):
        return x
        
class match_list(ListAPIView):
    permission_classes = [AllowAny]

    serializer_class = ListMatchSerializers
    # queryset = Match.objects.all()
    def get(self, request, *args, **kwargs):
        queryset = reversed(Match.objects.all())
        previous = []
        live = []
        upcomming = []
        live_date = datetime.combine(datetime.today(), datetime.max.time())

        
        mycol = mydb["cricket_api_match"]
        for match in mycol.find():
            if match["is_toss"]  == True:
                if match["batting_team_id"]:    
                    # ---------------------------------------------------------- batting team stats -----------------------------------------------------------------
                    batting_team = get_team_name(int(match["batting_team_id"]))
                    bat_obj = get_run_of_team(match, batting_team)
                    # ---------------------------------------------------------- bowling team stats -----------------------------------------------------------------
                    bowling_team = get_team_name(int(match["bowing_team_id"]))
                    bowl_obj = get_run_of_team(match, bowling_team)

                
                match_obj = {
                        "match_id":match["id"],
                        "umpire_id":match["umpire_id"],
                        "result":match["result"],
                        "total_over":match["over"],
                        "batting_team": bat_obj["batting_team_name"],
                        "ball":match["ball"],
                        "over":match["over"],
                        "venue":match["venue"],
                        "batting_team_players":{
                            "name":bat_obj["batting_team_name"],
                            "image":bat_obj["batting_team_image"],
                            "run":bat_obj["run"],
                            "wicket":bat_obj["wicket"],
                            "over":bat_obj["over"],
                            "ball_number":bat_obj["ball_number"],

                            },
                        "bowing_team_players":{
                            "name":bowl_obj["batting_team_name"],
                            "image":bowl_obj["batting_team_image"],
                            "run":bowl_obj["run"],
                            "wicket":bowl_obj["wicket"],
                            "over":bowl_obj["over"],
                            "ball_number":bowl_obj["ball_number"],

                            },
                        
                        }
            if match["is_toss"] == False and match["match_finish"] == False:
                # team1_image = ''
                #     if str(match.team1.team_image):
                #         team1_image = str(match.team1.team_image)
                #     team2_image = ''
                #     if str(match.team2.team_image):
                #         team2_image = str(match.team2.team_image)
                team1 = get_team_name(match['team1_id'])
                team2 = get_team_name(match['team2_id'])
                match_obj = {
                    "match_id":match["id"],
                    "umpire_id":match["umpire_id"],
                    "result":match["result"],
                    "team1_id":match["team1_id"] ,
                    "team1_name":team1["team_name"],
                    "team1_image":team1['team_image'],
                    "team2_id":match["team2_id"] ,
                    "team2_name":team2["team_name"],
                    "team2_image":team2['team_image'],
                    "over":match["over"],
                    "venue":match["venue"],
                    "date":match["date"],
                    "time":match["time"],
                    }
            if match["match_finish"] == True:
                previous.append(match_obj)
                print('previous')
            if match["match_finish"] == False and match["is_toss"] == True:

                print('live')
                live.append(match_obj)
            if match["is_toss"] == False:
                # if  date > datetime.now():
                print('upcomming')
                upcomming.append(match_obj)
            
        return Response(data={"status": status.HTTP_200_OK,
                              "error": False,
                              "message": "All teams list",
                              "result": {
                                "previous":previous,
                                "live":live,
                                "upcomming":upcomming,
                              }},
                        status=status.HTTP_200_OK,)