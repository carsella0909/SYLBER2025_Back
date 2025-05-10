from models import User, Room, Game
from random import shuffle

from sio.game import GameNamespace


class CatchVoice(GameNamespace):
    def __init__(self, room: Room, users: list[User]):
        self.room = room
        self.users = users
        shuffle(self.users)
        self.game = Game(
            room_id=self.room.id,
        )
        self.current_round = 0

    def get_user(self, sid):
        # Get the user from the sid in roomusers and validate is in this game
        ...

    def next_round(self):
        # Start the game round
        self.current_round += 1
        if self.current_round % 2 == 0:
            self.audio_round()
        else:
            self.text_round()

    def broadcast(self, event, *args, **kwargs):
        # Broadcast the event to all users in the room
        for user in self.users:
            self.emit(event, *args, to=user.id, **kwargs)

    async def text_round(self):
        # TODO : Implement the text round
        self.broadcast('round', {
            'round': self.current_round,
            'type': 'text'
        })

    async def on_text(self, sid, data):
        ...

    def audio_round(self):
        # TODO : Implement the audio round
        ...

    async def on_audio(self, sid, data):
        # sid를 통해 roomuser 정보를 가져옴
        # roomuser와 room 을 join하여 game id를 가져옴
        # game id를 통해 game 정보를 가져옴
        # game id를 통해 game log를 가져옴
        # game log를 저장
        # game을 update
        ...