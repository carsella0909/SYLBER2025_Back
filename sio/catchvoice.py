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
        #users: random circular list
        self.game = Game(
            room_id=self.room.id,
        )
        self.current_round = 0

        #CatchVoiceRound arr
        self.rounds = []

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
        catchvoiceround = CatchVoiceRound(self, self.current_round)
        self.rounds.append(catchvoiceround)
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
            [self._timeout(self.game.time_limit), self.catch_voice_round.round_done.wait()],
            return_when=asyncio.FIRST_COMPLETED
        )


    def audio_round(self):
        self.broadcast('round', {
            'round': self.current_round,
            'type': 'audio'
        })


    async def _timeout(self, timeout):
        # Wait for the timeout
        await asyncio.sleep(timeout)


class CatchVoiceRound:
    def __init__(self, game: CatchVoice, round_number: int):
        self.game = game
        #data_dict: {user_id: data}
        self.data_dict = {}
        #round_number: current round_number
        self.round_number = round_number
        self.round_done = asyncio.Event()
        self.round_done.clear()

    def start(self):
        new_users = self.game.users
        for i in range(len(new_users)):
            new_users[i] = self.game.users[(i + self.round_number) % len(self.game.users)]

