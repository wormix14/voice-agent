# main.py or api/token.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict
import os
import time
from livekit import api
from dotenv import load_dotenv
import json
from fastapi.middleware.cors import CORSMiddleware

load_dotenv(".env.local")
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TokenRequest(BaseModel):
    room_name: Optional[str] = None
    participant_identity: Optional[str] = None
    participant_name: Optional[str] = None
    topic: str 
    participant_metadata: Optional[str] = None
    participant_attributes: Optional[Dict[str, str]] = None


@app.post("/api/token", status_code=201)
async def get_token(request: TokenRequest):
    try:
        # TODO: Add your authentication here
        # from fastapi import Depends, Header
        # async def verify_token(authorization: str = Header(...)):
        #     # Verify JWT or session token
        #     pass
        # Then add: token_data: dict = Depends(verify_token)
        
        api_key = os.getenv('LIVEKIT_API_KEY')
        api_secret = os.getenv('LIVEKIT_API_SECRET')
        server_url = os.getenv('LIVEKIT_URL')
        
        if not all([api_key, api_secret, server_url]):
            raise HTTPException(
                status_code=500,
                detail='Server configuration error'
            )
        
        room_name = request.room_name or f'room-{int(time.time())}'
        participant_identity = request.participant_identity or f'user-{int(time.time())}'
        participant_name = request.participant_name or 'User'
        participant_metadata = {"metadata": request.participant_metadata,
                                "topic": request.topic }
        
        token = api.AccessToken(api_key, api_secret) \
            .with_identity(participant_identity) \
            .with_name(participant_name) \
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room_name,
                can_publish=True,
                can_subscribe=True,
            )
            ) \
            .with_room_config(api.RoomConfiguration(
                agents=[api.RoomAgentDispatch(
                    agent_name="my-agent",
                    metadata=json.dumps(participant_metadata))])
            )

        if request.participant_attributes:
            token = token.with_attributes(request.participant_attributes)
            
        
        participant_token = token.to_jwt()
        
        return {
            'server_url': server_url,
            'participant_token': participant_token,
            'topic': participant_metadata['topic']
        }
    except Exception as e:
        print(f'Token generation error: {e}')
        raise HTTPException(
            status_code=500,
            detail='Failed to generate token'
        )