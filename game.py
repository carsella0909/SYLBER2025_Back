from socketio import AsyncNamespace
from models import session, User, Room, Game, RoomUser


class GameNamespace(AsyncNamespace):
    def __init__(self, namespace=None):
        super().__init__(namespace)
        games = {}
        # game_id : CatchVoice



    async def on_disconnect(self, sid, reason):
        ...
        # 유저가 방에서 나갈 때 sid를 통해 roomuser 정보를 가져옴
        # room id를 통해 room 정보를 가져옴
        # room state가 playing이 아니면 roomuser가 방을 나간 것으로 간주
        # room state가 playing이면 roomuser의 is_connected를 false로 바꿈
        roomuser = session.query(RoomUser).filter(RoomUser.sid == sid).first()
        if not roomuser:
            return
        room = roomuser.room
        if not room:
            return
        user = roomuser.user
        if not user:
            return
        roomuser.leaving_room(room, user)

    async def on_connect(self, sid, environ):
        ...
        # 유저가 방에 들어갈 때 sid를 통해 roomuser 정보를 가져옴
        # room id를 통해 room 정보를 가져옴
        # is connected가 false면 재접속한 것으로 간주하고
        # roomuser의 is_connected를 true로 바꿈
        # is connected가 true면 중복접속으로 간주하고
        # 이미 저장된 sid의 연결을 끊고 새로운 sid를 저장
        roomuser = session.query(RoomUser).filter(RoomUser.sid == sid).first()
        if not roomuser:
            return
        room = roomuser.room
        if not room:
            return
        if roomuser.is_connected:
            # 중복접속
            roomuser.sid = sid
            session.commit()
        else:
            # 재접속
            roomuser.is_connected = True
            session.commit()

    async def on_join(self, sid, data):
        ...
        # 유저가 방에 들어갈 때 data에서 유저 id와 room code를 가져옴
        # room code를 통해 get_room room 정보를 가져옴
        # room에 유저를 추가하고(roomuser에 sid도 추가)
        # 방에 있는 모든 유저에게 방에 유저가 들어갔다는 것을 알림(update)
        user_id = data.get("user_id")
        room_code = data.get("room_code")
        if not user_id or not room_code:
            return
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            return
        room = session.query(Room).filter(Room.code == room_code).first()
        if not room:
            return
        if room.status == "inactive":
            return
        if room.status == "playing":
            return
        # 방에 유저가 이미 있는지 확인
        roomuser = session.query(RoomUser).filter(RoomUser.user_id == user.id, RoomUser.room_id == room.id).first()
        if roomuser:
            # 방에 유저가 이미 있는 경우
            # 방에 유저가 들어간 것으로 간주하고
            # 방에 있는 모든 유저에게 방에 유저가 들어갔다는 것을 알림(update)
            roomuser.sid = sid
            for roomuser in room.room_users:
                await self.emit("user_joined", {"username": user.username}, room=roomuser.sid)
            session.commit()
        else:
            return

    async def on_leave(self, sid, data):
        ...
        # 유저가 방에서 나갈 때 sid를 통해 roomuser 정보를 가져옴
        # room id를 통해 room 정보를 가져옴
        # roomuser를 삭제하고
        # 방에 있는 모든 유저에게 방에서 나갔다는 것을 알림(update)
        # 방에 유저가 없거나 host 유저면 방을 삭제
        roomuser = session.query(RoomUser).filter(RoomUser.sid == sid).first()
        if not roomuser:
            return
        room = roomuser.room
        if not room:
            return
        user = roomuser.user
        if not user:
            return
        roomuser.leaving_room(room, user)

    async def on_start(self, sid, data):
        roomuser = session.query(RoomUser).filter(RoomUser.sid == sid).first()
        if not roomuser:
            return
        room = roomuser.room
        if not room:
            return
        user = roomuser.user
        if not user:
            return
        if user.id == room.host_id:
            # 방을 시작
            room.status = "playing"
            session.commit()
            #


    async def leaving_room(self, room, user):
        if room.status != "playing":
            if user.id == room.host_id:
                for user in room.room_users:
                    await self.emit("room_deleted", {"code": room.code}, room=user.sid)
                room.delete()
            else:
                roomusers = session.query(RoomUser).filter(RoomUser.room_id == room.id).all()
                if not roomusers:
                    for user in room.room_users:
                        await self.emit("room_deleted", {"code": room.code}, room=user.sid)
                        room.delete()
                else:
                    await self.emit("user_left", {"username": user.username}, room=room.code)
                    room.leave(user)

        else:
            self.is_connected = False
            session.commit()

    async def on_text(self, sid, data):
        ...

    async  def on_audio(self, sid, data):
        file = data.get("file")
        if not file:
            return
        with open(f"tmp/{sid}.wav", "wb") as f:
            f.write(file)
