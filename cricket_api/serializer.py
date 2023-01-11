from rest_framework import serializers
from .models import *



class LoginUserSerializers(serializers.ModelSerializer):
    # email=serializers.EmailField(required=False)
    # password=serializers.CharField(required=False)
    # # login_type=serializers.CharField(required=False)
    # uuid=serializers.CharField(required=False)
    # mobile_no=serializers.CharField(required=False)
    class Meta:
        model=User
        fields=[]


class CreateUserSerializers(serializers.ModelSerializer):
    uuid = serializers.CharField(required=False)
    username=serializers.CharField(required=True)
    password=serializers.CharField(required=False)
    email=serializers.EmailField(required=False)
    country=serializers.CharField(required=False)
    profile_image=serializers.ImageField(required=False)
    player_type=serializers.CharField(required=True)
    batsman_type=serializers.CharField(required=False)
    bowler_type=serializers.CharField(required=False)
    jersey_no=serializers.CharField(required=False)
    class Meta:
        model= User
        fields= ["uuid","username","password","profile_image","email","country","player_type","batsman_type","bowler_type","jersey_no"]

class UpdateUserSerializers(serializers.ModelSerializer):
    # username=serializers.CharField(required=False)
    # address=serializers.CharField(required=False)
    # country=serializers.CharField(required=False)
    # profile_image=serializers.CharField(required=False)
    # player_type=serializers.CharField(required=False)
    # batsman_type=serializers.CharField(required=False)
    # bowler_type=serializers.CharField(required=False)
    # profile_image=serializers.ImageField(required=False)
    class Meta:
        model= User
        fields= ["username","address","country","player_type","batsman_type","bowler_type"]
        # fields= ["username","address","profile_image","country","player_type","batsman_type","bowler_type"]

class ListUserSerializers(serializers.ModelSerializer):
    # total_out = serializers.SerializerMethodField()

    class Meta:
        model= User
        fields= ["uuid","username","jersey_no","email","mobile_no","password","address","country","device_token","profile_image","profile_image_url","cover_image","player_type","batsman_type","bowler_type","total_innings","total_matches","total_run","total_wicket","total_ball","total_4","total_6","total_50","total_100","average"]

    # def get_total_out(self, obj):
    #     return len(Deliveries.objects.filter(batter=obj,isWicketDelivery=True))


class AllUserSerializers(serializers.ModelSerializer):
    username=serializers.CharField(required=True)
    profile_image=serializers.CharField(required=False)
    player_type=serializers.CharField(required=False)

    class Meta:
        model= User
        fields= ["id","username","first_name","last_name","profile_image","player_type"]

class Players(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','profile_image','player_type']

class ListTeamSerializers(serializers.ModelSerializer):
    player = Players(read_only=True,many=True)

    class Meta:
        model= Team
        fields= ['id','team_name','team_image','caption','wicket_keeper','player']

class CommentarySerializers(serializers.ModelSerializer):
    # player = Players(read_only=True,many=True)

    class Meta:
        model= Commentary
        fields= '__all__'

class Sender(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','profile_image']

# class ListchatSerializers(serializers.ModelSerializer):
#     # sender = Sender(read_only=True)
#     # sender_name= serializers.ReadOnlyField(source='sender.username')
#     # sender_image= serializers.ReadOnlyField(source='sender.profile_image.url')
#     # team1_id= serializers.ReadOnlyField(source='team1.id')
#     class Meta:
#         model= ChatModel
#         fields= ["sender","message","thread_name","timestamp",]

class MatchDetailSerializers(serializers.ModelSerializer):
    player = Players(read_only=True,many=True)
    class Meta:
        model= Match
        fields= "__all__"



class BatsmanUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','total_run','player_type']


class CreateTeamSerializers(serializers.ModelSerializer):
    team_name=serializers.CharField(required=True)
    team_image=serializers.CharField(required=False)
    caption=serializers.CharField(required=True)
    wicket_keeper=serializers.CharField(required=True)
    player=serializers.CharField(required=True)
    
    class Meta:
        model= Team
        fields= ["team_name","team_image","caption","wicket_keeper","player"]

        

class SubscriptionSerializers(serializers.ModelSerializer):
    user =  serializers.CharField(required=True)
    strip_user_id = serializers.CharField(required=True)
    payment_id = serializers.CharField(required=True)
    subscription_type = serializers.CharField(required=True)
    duration = serializers.CharField(required=True)
    start_time = serializers.CharField(required=False)
    end_time = serializers.CharField(required=False)
    
    
    class Meta:
        model= Subscription
        fields= "__all__"


class CreateMatchSerializers(serializers.ModelSerializer):
    
    team1=serializers.CharField(required=True)
    team2=serializers.CharField(required=True)
    date=serializers.DateField(required=False)
    time=serializers.TimeField(required=False)
    venue=serializers.CharField(required=True)
    is_toss=serializers.IntegerField(required=True)
    umpire=serializers.CharField(required=False)
    tose_winner=serializers.CharField(required=False)
    toss_decision=serializers.CharField(required=False)
    opener=serializers.CharField(required=False)
    bowler=serializers.CharField(required=False)
    over=serializers.IntegerField(required=True)

    class Meta:
        model= Match
        fields= ["team1","team2","date","time","venue","umpire","tose_winner","toss_decision","opener","bowler","over","is_toss"]

class CheckPlayerSerializers(serializers.ModelSerializer):


    class Meta:
        model= Match
        fields= []

class BowlerSerializers(serializers.ModelSerializer):
    team=serializers.CharField(required=True)
    match=serializers.CharField(required=True)
    bowler=serializers.CharField(required=True)

    class Meta:
        model=Match
        fields=["team","match","bowler"]
        
class TeamUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','total_run','player_type']

class DeleveriesSerializers(serializers.ModelSerializer):

    class Meta:
        model= Deliveries
        fields= '__all__'
class DynamicTeamSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','total_run','player_type']

class UndoDeleveriesSerializers(serializers.ModelSerializer):

    class Meta:
        model= Deliveries
        fields= []
class ListMatchSerializers(serializers.ModelSerializer):
    team1_id= serializers.ReadOnlyField(source='team1.id')
    team2_id= serializers.ReadOnlyField(source='team2.id')
    team1_name= serializers.ReadOnlyField(source='team1.team_name')
    team2_name= serializers.ReadOnlyField(source='team2.team_name')
    team1_image= serializers.ReadOnlyField(source='team1.team_image')
    team2_image= serializers.ReadOnlyField(source='team2.team_image')
    umpire_id= serializers.ReadOnlyField(source='umpire.id')
    umpire_name= serializers.ReadOnlyField(source='umpire.username')
    umpire_image= serializers.ReadOnlyField(source='umpire.profile_image')
    
    class Meta:
        model= Match
        # fields= ['team1_id','team1_name','team1_image','team2_id','team2_name','team2_image','umpire_id','umpire_name','umpire_image','date','time','venue','tose_winner','toss_decision','opener','bowler','over','match_finish']
        fields= "__all__"



class Teams(serializers.ModelSerializer):
    class Meta:
        model = Team
        fields = ['id','team_name','team_image']


class ListMatchSerializers2(serializers.ModelSerializer):
    batting_team= serializers.ReadOnlyField(source='batting_team.team_name')
    bowing_team= serializers.ReadOnlyField(source='bowing_team.team_name')
    # team1_name= serializers.ReadOnlyField(source='team1.team_name')
    # team2_name= serializers.ReadOnlyField(source='team2.team_name')
    # team1_image= serializers.ReadOnlyField(source='team1.team_image')
    # team2_image= serializers.ReadOnlyField(source='team2.team_image')
    umpire_id= serializers.ReadOnlyField(source='umpire.id')
    # owner = PrimaryKeyRelatedField(queryset=User.objects.all())
    # umpire_name= serializers.ReadOnlyField(source='umpire.username')
    # umpire_image= serializers.ReadOnlyField(source='umpire.profile_image')
    batting_team_players = serializers.SerializerMethodField()
    bowling_team_players = serializers.SerializerMethodField()
    # team1 = Teams(read_only=True,many=True,Match.team1)
    
    class Meta:
        model= Match
        # fields= ['team1_id','team1_name','team1_image','team2_id','team2_name','team2_image','umpire_id','umpire_name','umpire_image','date','time','venue','tose_winner','toss_decision','opener','bowler','over','match_finish']
        # fields= "__all__"
        fields= ["id","umpire_id","result","batting_team","bowing_team","ball","over","venue","batting_team_players","bowling_team_players"]

    def get_batting_team_players(self, obj):
        if obj.batting_team:
            stat = Deliveries.objects.filter(match=obj,BattingTeam=obj.batting_team)
            name = str(obj.batting_team.team_name) if obj.batting_team.team_name else ''
            image = str(obj.batting_team.team_image.url) if obj.batting_team.team_image else ''
            run =  stat.aggregate(Sum('total_run'))["total_run__sum"]
            wicket = stat.filter(isWicketDelivery__in=[True]).count()
            # over
            ball_number = 0
            over = 0
            if stat.filter(innings=obj.innings).last():
                last_ball = stat.filter(innings=obj.innings).last()
                ball_number = last_ball.ballnumber
                over = last_ball.overs
        else:
            name = ''
            image = ''
            run =  0
            wicket = 0
            ball_number = 0
            over = 0

        return {
            # 'ida': obj.batting_team.id,
            'name': name,
            'image': image,
            'run': run,
            'wicket': wicket,
            'ball_number': ball_number,
            'over': over,
            }
    def get_bowling_team_players(self, obj):
        if obj.bowing_team:
            stat = Deliveries.objects.filter(match=obj,BowlingTeam=obj.bowing_team)
            name = str(obj.bowing_team.team_name) if obj.bowing_team.team_name else ''
            image = str(obj.bowing_team.team_image.url) if obj.bowing_team.team_image else ''
            run =  stat.aggregate(Sum('total_run'))["total_run__sum"]
            wicket = stat.filter(isWicketDelivery__in=[True]).count()
            # over
            ball_number = 0
            over = 0
            if stat.filter(innings=obj.innings).last():
                last_ball = stat.filter(innings=obj.innings).last()
                ball_number = last_ball.ballnumber
                over = last_ball.overs
        else:
            name = ''
            image = ''
            run =  0
            wicket = 0
            ball_number = 0
            over = 0

        return {
            # 'ida': obj.batting_team.id,
            'name': name,
            'image': image,
            'run': run,
            'wicket': wicket,
            'ball_number': ball_number,
            'over': over,
            }
"""
match_id
umpire_id = serializers.ReadOnlyField(source='umpire.id')
result
total_over
batting_team = serializers.ReadOnlyField(source='batting_team.name')
ball
over
venue

"""



class ForgotpasswordSerializer(serializers.ModelSerializer):
    email=serializers.EmailField(required=True)
    class Meta:
        model=User
        fields=["email"]
        
class BatsmanSerializers(serializers.ModelSerializer):
    team=serializers.CharField(required=True)
    match=serializers.CharField(required=True)
    opener=serializers.CharField(required=True)

    class Meta:
        model=Match
        fields=["team","match","opener"]



class ChangeInningSerializers(serializers.ModelSerializer):
    opener=serializers.CharField(required=False)
    class Meta:
        model=Match
        fields=["innings","opener","batting_team","bowing_team","bowler"]


class UpdateMatchSerializers(serializers.ModelSerializer):
    date=serializers.DateField(required=False)
    time=serializers.TimeField(required=False)
    
    tose_winner=serializers.CharField(required=True)
    batting_team=serializers.CharField(required=True)
    bowing_team=serializers.CharField(required=True)
    opener=serializers.CharField(required=True)
    bowler=serializers.CharField(required=True)
    # over = serializers.CharField(required=False)
    class Meta:
        model=Match
        fields=["date","time","tose_winner","batting_team","bowing_team","opener","bowler"]

class ChangeUmpireSerializers(serializers.ModelSerializer):
    umpire=serializers.CharField(required=False)
    
    class Meta:
        model=Match
        fields=["umpire"]

class DuplicatePlayerSerializers(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=[]



class TopUserSerializers(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','total_run','player_type','total_wicket','country']