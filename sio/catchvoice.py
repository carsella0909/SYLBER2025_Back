import asyncio

from models import *
from random import shuffle

from sio.game import GameNamespace


class CatchVoice:
    def __init__(self, socket, room: Room, users: list[User]):
        self.socket = socket
        self.room = room
        self.users = users
        shuffle(self.users)
        self.game = Game(
            room_id=self.room.id,
        )
        self.current_round = 0

    def get_user(self, sid):
        # Get the user from the sid in roomusers and validate is in this game
        roomuser = session.query(RoomUser).filter(RoomUser.sid == sid).first()
        if not roomuser:
            return None
        if roomuser.room_id != self.room.id:
            return None
        if roomuser.user_id not in [user.id for user in self.users]:
            return None
        return roomuser.user

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
            self.socket.emit(event, *args, to=user.id, **kwargs)

    async def text_round(self):
        self.broadcast('round', {
            'round': self.current_round,
            'type': 'text'
        })
        await asyncio.wait(
            [self._timeout(30), self.round_done.wait()],
            return_when=asyncio.FIRST_COMPLETED
        )

    def audio_round(self):
        # TODO : Implement the audio round
        ...
