from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import render
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.conf import settings
from dota2.handlers.GameHandler import GamesHandler

# Create your views here.

def ProcessCSGOOngoingGame(game):
    data = dict()
    
    if "allplayers" in game:    
        data = {
            "status": {
                "is_going": True
            },
            "game": {
                "map": game["map"]["name"],
                "round": game["map"]["round"]   
            }
        }
        
        players_data = []
        for player in game["allplayers"].values():
            weapons = []
            for weapon in player["weapons"].values():
                weapons.append({
                    "name": weapon["name"][7:],
                    "url": f"http://localhost:8000/config/{weapon['name']}.svg"
                })
            
            players_data.append({
                "name": player["name"],
                "team": player["team"],
                "state": {
                    "health": player["state"]["health"],
                    "armor": player["state"]["armor"],
                    "money": player["state"]["money"]
                },
                "stats": player["match_stats"],
                "weapons": weapons
            })
            
        data["game"]["players"] = [players_data]
        return data
        
    else:   
        data = {
            "status": {
                "is_going": False  
            },
            "game": {
                "msg": "You're in a menu or watching private match"
            }
        }
        
        return data
        


@api_view(['POST'])
def ProcessDotaGame(request):
    data = request.data
    room_group_name = "gsi_%s" % data['auth']['token']
    
    game_handler = GamesHandler(settings.DOTA_API_KEY)
    normalized_data = game_handler.extract_data_from_ongoing_game(data)
    normalized_data["provider"] = "dota"
    
    # send message through webscoket connection with client
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        room_group_name, 
        {
            "type": "gsi_message",
            "message": normalized_data
        }
    )

    return Response({"msg": room_group_name}, status.HTTP_200_OK)

@api_view(['POST'])
def ProcessCSGOGame(request):
    data = request.data
    room_group_name = "gsi_%s" % data['auth']['token']
    
    normalized_data = ProcessCSGOOngoingGame(data)
    normalized_data["provider"] = "csgo"
    
    # send message through webscoket connection with client
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        room_group_name, 
        {
            "type": "gsi_message",
            "message": normalized_data
        }
    )

    return Response({"msg": room_group_name}, status.HTTP_200_OK)
