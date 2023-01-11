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