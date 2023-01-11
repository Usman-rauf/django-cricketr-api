# import json
# from .models import *
# from .serializer import *
# from channels.generic.websocket import AsyncWebsocketConsumer
# from asgiref.sync import async_to_sync, sync_to_async
# from asgiref.sync import sync_to_async




# class PersonalChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         # my_id = self.scope['user'].id
#         # other_user_id = self.scope['url_route']['kwargs']['id']
#         my_id = self.scope['url_route']['kwargs']['sender']
#         other_user_id = self.scope['url_route']['kwargs']['rec']

#         # print(sender,'-------------------------')
#         # print(rec,'-------------------------')
#         if int(my_id) > int(other_user_id):
#        	    self.room_name = f'{my_id}-{other_user_id}'
#         else:
#             self.room_name = f'{other_user_id}-{my_id}'


#         self.room_group_name = "chat_%s" % self.room_name

#         await self.channel_layer.group_add(
#         	self.room_group_name,
#         	self.channel_name

#         )
        
#         await self.accept()
#         result = await self.get_user(other_user_id, my_id)

#         # print(my_id)
#         # print(user_obj, my_id)

        
#         # ---------------------------------------------------------- Send message to WebSocket -----------------------------------------------------------------
#         await self.send(text_data=json.dumps({
#                               "user": result[1],
#                               "count": len(result[0]),
#                               "result": result[0],
#                               }))

#     async def disconnect(self, close_code):
#         # Leave room group
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     # ---------------------------------------------------------- Receive message from WebSocket -----------------------------------------------------------------
#     async def receive(self, text_data):
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#         sender = text_data_json["sender"]
#         # Saving the messages
#         await self.save_message(sender, self.room_group_name, message)

#         # Send message to room group
#         await self.channel_layer.group_send(
#             self.room_group_name, {"type": "chat_message", "message": message, "sender": sender}
#         )
#     # ---------------------------------------------------------- Receive message from room group -----------------------------------------------------------------
#     async def chat_message(self, event):
#         # message = event["message"]
#         # sender = event["sender"]

#         my_id = self.scope['url_route']['kwargs']['sender']
#         other_user_id = self.scope['url_route']['kwargs']['rec']
#         result = await self.get_user(other_user_id, my_id)

#         # print(my_id)
#         # print(user_obj, my_id)

        
#         # ---------------------------------------------------------- Send message to WebSocket -----------------------------------------------------------------
#         await self.send(text_data=json.dumps({
#                               "user": result[1],
#                               "count": len(result[0]),
#                               "result": result[0],
#                               }))

#     @sync_to_async
#     def save_message(self, username, thread_name, message):
#         user = User.objects.filter(id=username,is_delete__in=[False]).first()
#         ChatModel.objects.create(
#             sender=user, message=message, thread_name=thread_name)
    

#     # ---------------------------------------------------------- Get all message by group -----------------------------------------------------------------
#     @sync_to_async
#     def get_user(self, other_user_id, my_id):
#         user_obj =  User.objects.get(id=other_user_id)
#         if my_id > other_user_id:
#             thread_name = f'chat_{my_id}-{other_user_id}'
#         else:
#             thread_name = f'chat_{other_user_id}-{my_id}'
#         message_objs = ChatModel.objects.filter(thread_name=thread_name)

#         j_data = ListchatSerializers(message_objs, many=True).data


#         usr_obj={
#             "user_id":user_obj.id,
#             "user_username":user_obj.username,
#             "user_profile_image":user_obj.profile_image.url,
#         }
#         return j_data, usr_obj