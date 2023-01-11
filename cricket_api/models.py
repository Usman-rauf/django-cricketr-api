from time import time
from django.db import models
from django.contrib.auth.models import AbstractUser
from datetime import datetime,  date
from datetime import date

"""Uset authentication models"""


PLAYER_TYPE_CHOICE=(
    ("BATSMAN","BATSMAN"),
    ("BOWLER","BOWLER"),
    ("WICKET-KEEPER","WICKET-KEEPER"),
    ("ALL-ROUNDER","ALL-ROUNDER"),
)

BATSMAN_TYPE_CHOICE=(
    ("RIGHT HAND BATSMAN","RIGHT HAND BATSMAN"),
    ("LEFT HAND BATSMAN","LEFT HAND BATSMAN"),
)
BOWLER_TYPE_CHOICE=(
    ("RIGHT ARM PACE/SEAM BOWLING","RIGHT ARM PACE/SEAM BOWLING"),
    ("LEFT ARM PACE/SEAM BOWLING","LEFT ARM PACE/SEAM BOWLING"),
    ("RIGHT ARM SPIN BOWLING","RIGHT ARM SPIN BOWLING"),
    ("LEFT ARM SPIN BOWLING","LEFT ARM SPIN BOWLING"),
)



def upload_to(instance, filename):
    return 'images/{filename}'.format(filename=filename)

class User(AbstractUser):
    USERNAME_FIELD = 'id'
    uuid=models.CharField(max_length=100, null=True,blank=True)
    username=models.CharField(max_length=20, null=True,blank=True,unique= False, default='')
    jersey_no=models.CharField(max_length=20, null=True,blank=True)
    email=models.EmailField(max_length=100,null=True,blank=True)
    mobile_no=models.CharField(max_length=20,null=True,blank=True)
    password=models.CharField(max_length=200,null=True,blank=True)
    address=models.CharField(max_length=300,null=True,blank=True)
    country=models.CharField(max_length=200,null=True,blank=True)
    device_token=models.CharField(max_length=200,null=True,blank=True)
    profile_image=models.ImageField(upload_to=upload_to,null=True,blank=True)
    cover_image=models.ImageField(upload_to=upload_to,null=True,blank=True)
    profile_image_url=models.CharField(max_length=5000,null=True,blank=True)
    player_type=models.CharField(max_length=100,choices=PLAYER_TYPE_CHOICE,null=True,blank=True)
    batsman_type=models.CharField(max_length=100,choices=BATSMAN_TYPE_CHOICE,null=True,blank=True)
    bowler_type=models.CharField(max_length=100,choices=BOWLER_TYPE_CHOICE,null=True,blank=True)
    total_innings=models.IntegerField(null=True,blank=True,default=0)
    total_matches=models.IntegerField(null=True,blank=True,default=0)
    total_run=models.IntegerField(null=True,blank=True,default=0)
    total_wicket=models.IntegerField(null=True,blank=True,default=0)
    total_ball=models.IntegerField(null=True,blank=True,default=0)
    total_4=models.IntegerField(null=True,blank=True,default=0)
    total_6=models.IntegerField(null=True,blank=True,default=0)
    total_50=models.IntegerField(null=True,blank=True,default=0)
    total_100=models.IntegerField(null=True,blank=True,default=0)
    average=models.IntegerField(null=True,blank=True,default=0)

    is_social=models.BooleanField(default=False)
    otp=models.CharField(max_length=10,null=True,blank=True)
    is_delete=models.BooleanField(default=False)
    is_pro=models.BooleanField(default=False)




    
    def __str__ (self):
        return f"{self.username}"
"""
highest score
total catch
total_win
average = runs/out
"""



# class ChatModel(models.Model):
#     sender = models.ForeignKey(User,related_name='sender',on_delete=models.CASCADE)
#     message = models.TextField(null=True, blank=True)
#     thread_name = models.CharField(null=True, blank=True, max_length=50)
#     timestamp = models.DateTimeField(auto_now_add=True)

#     def __str__(self) -> str:
#         return self.message


class Usertoken(models.Model):
    user=models.ForeignKey(User,related_name='token',on_delete=models.CASCADE)
    token=models.CharField(max_length=500,null=True,blank=True)




"""Cricket models"""

class Team(models.Model):
    team_name=models.CharField(max_length=500,null=True,blank=True)
    team_image=models.ImageField(upload_to=upload_to,max_length=500,null=True,blank=True)
    best_score=models.IntegerField(null=True,blank=True,default=0)
    win_count=models.IntegerField(null=True,blank=True,default=0)
    lose_count=models.IntegerField(null=True,blank=True,default=0)
    total_match=models.IntegerField(null=True,blank=True,default=0)
    caption=models.ForeignKey(User,related_name='caption',on_delete=models.CASCADE)
    wicket_keeper=models.ForeignKey(User,related_name='keeper',on_delete=models.CASCADE)
    player=models.ManyToManyField(User)
    created_by=models.ForeignKey(User,related_name='team_manager',on_delete=models.CASCADE)
    def __str__ (self):
        return f"{self.team_name}"


# class TeamPlayer(models.Model):
#     team=models.ForeignKey(Team,related_name='team',on_delete=models.CASCADE)
  
from django.db.models import Sum

class Match(models.Model):

    team1 = models.ForeignKey(Team, related_name='team1', on_delete=models.CASCADE)
    team2 = models.ForeignKey(Team, related_name='team2', on_delete=models.CASCADE)
    winner = models.ForeignKey(Team, related_name='winner', on_delete=models.CASCADE,null=True,blank=True)
    result=models.CharField(max_length=255,null=True,blank=True)
    date=models.DateField(null=True,blank=True)
    time=models.TimeField(null=True,blank=True)
    venue= models.CharField(max_length=255,null=True,blank=True)
    umpire=models.ForeignKey(User,related_name='umpire',on_delete=models.CASCADE)
    tose_winner=models.ForeignKey(Team,related_name='tose_win',on_delete=models.CASCADE)
    toss_decision = models.CharField(max_length=100, null=True,blank=True)
    opener=models.ManyToManyField(User)
    bowler=models.ForeignKey(User,related_name='bowler',on_delete=models.CASCADE)
    over = models.IntegerField(null=True,blank=True,default=0)
    is_over = models.BooleanField(default=False)
    run = models.IntegerField(null=True,blank=True,default=0)
    wicket= models.IntegerField(null=True,blank=True,default=0)
    ball= models.IntegerField(null=True,blank=True,default=0)
    is_toss=models.BooleanField(default=False)
    match_finish=models.BooleanField(default=False)
    created_by=models.ForeignKey(User,related_name='match_manager',on_delete=models.CASCADE)
    batting_team=models.ForeignKey(Team,related_name='batting_team',on_delete=models.CASCADE,blank=True,null=True,)
    bowing_team=models.ForeignKey(Team,related_name='bowing_team',on_delete=models.CASCADE,blank=True,null=True,)
    innings	= models.IntegerField(default=1)
    schedule_datetime=models.DateTimeField(null=True,blank=True)
    def __str__(self):
        return self.team1.team_name + ' v/s ' + self.team2.team_name
    

    # def get_run_of_team(self):
    #     run = Deliveries.objects.filter(match=self,BattingTeam= self.batting_team).aggregate(Sum('total_run'))["total_run__sum"]
    #     if run == None:
    #         return 0
    #     return run
# class CurrentBatsman(models.Model):
#     team = models.ForeignKey(Team, on_delete=models.CASCADE)
#     match = models.ForeignKey(Match, on_delete=models.CASCADE)
#     batsman=models.ManyToManyField(User)
#     bowler = models.ForeignKey(User, on_delete=models.CASCADE)

class Deliveries(models.Model):
    match = models.ForeignKey(Match, related_name='match', on_delete=models.CASCADE)
    innings	= models.IntegerField(default=1)
    overs = models.IntegerField(default=0, blank=True, null=True)
    ballnumber = models.IntegerField(default=0, blank=True, null=True)
    batter = models.ForeignKey(User,related_name='batter',on_delete=models.CASCADE)
    bowler = models.ForeignKey(User,related_name='bowler_user',on_delete=models.CASCADE)
    on_striker	 = models.ForeignKey(User,related_name='on_striker',on_delete=models.CASCADE)
    non_striker	 = models.ForeignKey(User,related_name='non_striker',on_delete=models.CASCADE)
    extra_type	= models.CharField(max_length=20, blank=True, null=True)
    batsman_run	= models.IntegerField(default=0, blank=True, null=True)
    extras_run	= models.IntegerField(default=0, blank=True, null=True)
    total_run	= models.IntegerField(default=0, blank=True, null=True)
    non_boundary = models.BooleanField(default=False)
    isWicketDelivery = models.BooleanField(default=False)
    player_out	= models.ForeignKey(User,related_name='player_out',on_delete=models.CASCADE,null=True,blank=True)
    kind	= models.CharField(max_length=20, blank=True, null=True)
    fielders_involved	= models.ForeignKey(User,related_name='fielders_involved',on_delete=models.CASCADE,null=True,blank=True)
    BattingTeam =	models.ForeignKey(Team, related_name='BattingTeam', on_delete=models.CASCADE)
    BowlingTeam =	models.ForeignKey(Team, related_name='BowlingTeam', on_delete=models.CASCADE)
    SuperOver	 = models.BooleanField(default=False)


COMM_TYPE_CHOICE=(
    ("NORMAL","NORMAL"),
    ("EXTRA","EXTRA"),
    ("WICKET","WICKET"),
)

class Commentary(models.Model):
    match = models.ForeignKey(Match, related_name='match_id', on_delete=models.PROTECT)
    comment = models.CharField(max_length=500, blank=True, null=True)
    type=models.CharField(max_length=100,choices=COMM_TYPE_CHOICE,null=True,blank=True)
    over = models.IntegerField(default=0)
    stats = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return f"{self.comment}"


class Subscription(models.Model):
    user = models.ForeignKey(User, related_name='sub_usre', on_delete=models.PROTECT)
    strip_user_id = models.CharField(max_length=500, blank=True, null=True)
    payment_id = models.CharField(max_length=500, blank=True, null=True)
    subscription_type = models.CharField(max_length=500, blank=True, null=True)
    duration = models.IntegerField(default=0)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(blank=True, null=True)
    

    def __str__(self):
        return f"{self.comment}"

"""
ID	
innings	= models.IntegerField(default=1)
overs = models.IntegerField(default=0, blank=True, null=True)
ballnumber = models.IntegerField(default=0, blank=True, null=True)
batter = models.ForeignKey(User,related_name='batter',on_delete=models.CASCADE)
bowler = models.ForeignKey(User,related_name='bowler',on_delete=models.CASCADE)
non-striker	 = models.ForeignKey(User,related_name='non-striker',on_delete=models.CASCADE)
extra_type	= models.CharField(max_length=20, blank=True, null=True)
batsman_run	= models.IntegerField(default=0, blank=True, null=True)
extras_run	= models.IntegerField(default=0, blank=True, null=True)
total_run	= models.IntegerField(default=0, blank=True, null=True)
non_boundary = models.BooleanField(default=False)
isWicketDelivery = models.BooleanField(default=False)
player_out	= models.ForeignKey(User,related_name='batter',on_delete=models.CASCADE)
kind	= models.CharField(max_length=20, blank=True, null=True)
fielders_involved	= models.ForeignKey(User,related_name='batter',on_delete=models.CASCADE)
BattingTeam =	models.ForeignKey(Team, related_name='team1', on_delete=models.CASCADE)
SuperOver	 = models.BooleanField(default=False)
# City	
# Date	
# Season	
# MatchNumber	
# Team1	
# Team2	
# Venue	
# TossWinner	
# TossDecision	
# WinningTeam	
# WonBy	
# Margin	
# method	
# Player_of_Match	
# Team1Players	
# Team2Players	
# Umpire1	
# Umpire2	
# BowlingTeam
"""