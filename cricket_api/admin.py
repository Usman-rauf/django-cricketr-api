from django.contrib import admin
from .models import *

admin.site.register(Usertoken)
admin.site.register(Team)


class DeliveriesAdmin(admin.ModelAdmin):
    list_display = ('innings','overs','ballnumber','batter','bowler','non_striker','extra_type','batsman_run','extras_run','total_run','non_boundary','isWicketDelivery','player_out','kind','fielders_involved','BattingTeam','SuperOver',)
admin.site.register(Deliveries, DeliveriesAdmin)


class MatchAdmin(admin.ModelAdmin):
    list_display = ('date','time')
admin.site.register(Match)


class UserAdmin(admin.ModelAdmin):
    list_display = ('username','email','mobile_no', 'profile_image')
admin.site.register(User, UserAdmin)



