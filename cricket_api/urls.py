from django.urls import path
from cricket_api import user,team,match,tests,chat
from django.urls import re_path

from . import consumers


urlpatterns = [
    path('login', user.LoginAPIView.as_view(), name="login"),
    path('register', user.UserCreateAPIView.as_view(), name="register"),
    path('user_update/<int:pk>', user.UserUpdateAPIView.as_view(), name="update_user"),
    path('profile_update/<int:pk>', user.ProfileUpdateAPIView.as_view(), name="profile_update"),
    path('get_user/<int:pk>', user.GetUserAPIView.as_view(), name="get_user"),
    path('user_search/<str:username>', user.SearchUserAPIView.as_view(), name="user_search"),
    path('check_email', user.CheckEmailAPIView.as_view(), name="check_email"),
    path('check_mobile', user.CheckMobileAPIView.as_view(), name="check_mobile"),
    path('player_list', user.AllUserAPIView.as_view(), name="player_list"),
    path('user_delete/<int:pk>', user.UserDeleteAPIView.as_view(), name="user_delete"),
    path('forgot_password',user.ForgotPasswordAPIView.as_view(),name='forgot_password'),
    path('batsman_user', user.BatsmanUserAPIView.as_view(), name="batsman_user"),
    path('country_top_user_list',user.TopUserListAPIView.as_view(),name='country_top_user_list'),
    path('world_top_user_list',user.worldTopUserListAPIView.as_view(),name='world_top_user_list'),
    path('add_payment_detail',user.SubscriptionAPIView.as_view(),name='add_payment_detail'),


    path('team_list', team.TeamListAPIView.as_view(), name="team_list"),
    # path('live', team.livescoreAPIView.as_view(), name="live"),
    path('create_team', team.TeamCreateAPIView.as_view(), name="create_team"),
    path('team_update/<int:pk>', team.TeamUpdateAPIView.as_view(), name="team_update"),
    path('check_duplicate',team.DuplicatePlayerAPIView.as_view(),name='check_duplicate'),
    path('get_teams_players/<int:pk>',team.GetTeamPlayerAPIView.as_view(),name='get_teams_players'),


    # chat
    # path('chat_list/<int:pk>',chat.ChatListAPIView.as_view(),name='chat_list'),

    

    path('commentary/<int:pk>', match.CommentaryAPIView.as_view(), name="commentary"),
    path('create_match', match.MatchCreateAPIView.as_view(), name="create_match"),
    path('check_team_player', match.CheckPlayerAPIView.as_view(), name="check_team_player"),
    path('update_match/<int:pk>', match.MatchUpdateAPIView.as_view(), name="update_match"),
    path('change_umpire/<int:pk>', match.ChangeUmpireAPIView.as_view(), name="change_umpire"),
    path('update_batsman',match.UpdateBatsmanAPIView.as_view(),name='update_batsman'),
    path('update_bowler',match.UpdateBowlerAPIView.as_view(),name='update_bowler'),
    path('update_inning',match.UpdateInningAPIView.as_view(),name='update_inning'),
    path('dynamic_team',match.dynamicTeamAPIView.as_view(),name='dynamic_team'),
    path('delivery', match.DeleveriesAPIView.as_view(), name="delivery"),
    path('undo_delivery', match.UndoDeleveriesAPIView.as_view(), name="undo_delivery"),
    # path('match_list', match.Match_ListAPIView.as_view(), name="match_list"),
    path('match_details/<int:pk>', match.GetmatchAPIView.as_view(), name="match_details"),
    path('score_card/<int:pk>', match.GetscorecardAPIView.as_view(), name="score_card"),
    # path('change_password', user.ChangePasswordAPIView.as_view(), name="change_password"),
     path('end_match',match.EndMatchAPIView.as_view(),name='end_match'),

    # path('get_match/<int:pk>', tests.GetmatchAPIView.as_view(), name="get_match"),
     
    path('match_list', tests.match_list.as_view(), name="match_list"),
    # path('pre', tests.PreMatchesListAPIView.as_view(), name="pre"),
    # path('live', tests.LiveMatchesListAPIView.as_view(), name="live"),
    # path('up', tests.LiveMatchesListAPIView.as_view(), name="up"),

    
]

# websocket_urlpatterns = [
#     # re_path(r"ws/(?P<id>[0-9]+)/$", consumers.PersonalChatConsumer.as_asgi()),
#     path("ws/<int:sender>/<int:rec>", consumers.PersonalChatConsumer.as_asgi()),
# ]