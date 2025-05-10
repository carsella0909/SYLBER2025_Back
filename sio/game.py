from socketio import AsyncNamespace


class GameNamespace(AsyncNamespace):
    rooms = {}
    async def on_disconnect(self, sid, reason):
        ...
        # 유저가 방에서 나갈 때 sid를 통해 roomuser 정보를 가져옴
        # room id를 통해 room 정보를 가져옴
        # room state가 playing이면 roomuser가 방을 나간 것으로 간주
        # room state가 playing이 아니면 roomuser의 is_connected를 false로 바꿈


    async def on_connect(self, sid, environ):
        ...
        # 유저가 방에 들어갈 때 sid를 통해 roomuser 정보를 가져옴
        # room id를 통해 room 정보를 가져옴
        # is connected가 false면 재접속한 것으로 간주하고
        # roomuser의 is_connected를 true로 바꿈
        # is connected가 true면 중복접속으로 간주하고
        # 이미 저장된 sid의 연결을 끊고 새로운 sid를 저장

    async def on_join(self, sid, data):
        ...
        # 유저가 방에 들어갈 때 data에서 유저 id와 room code를 가져옴
        # room code를 통해 get_room room 정보를 가져옴
        # room에 유저를 추가하고(roomuser에 sid도 추가)
        # 방에 있는 모든 유저에게 방에 유저가 들어갔다는 것을 알림(update)

    async def on_leave(self, sid, data):
        ...
        # 유저가 방에서 나갈 때 sid를 통해 roomuser 정보를 가져옴
        # room id를 통해 room 정보를 가져옴
        # roomuser를 삭제하고
        # 방에 있는 모든 유저에게 방에서 나갔다는 것을 알림(update)
        # 방에 유저가 없거나 host 유저면 방을 삭제

    async def on_start(self, sid, data):
        ...
        # sid를 통해 roomuser 정보를 가져옴
        # room id를 통해 room 정보를 가져옴
        # user id와 host id가 같으면 방을 시작
        # 방을 시작하면 방의 상태를 playing으로 바꾸고
        # game을 생성
        # Round1을 emit

    async def on_text(self, sid, data):
        ...
        # sid를 통해 roomuser 정보를 가져옴
        # roomuser와 room 을 join하여 game id를 가져옴
        # game id를 통해 game 정보를 가져옴
        # game id를 통해 game log를 가져옴
        # game log를 저장
        # game을 update

    async def on_audio(self, sid, data):
        ...
        # sid를 통해 roomuser 정보를 가져옴
        # roomuser와 room 을 join하여 game id를 가져옴
        # game id를 통해 game 정보를 가져옴
        # game id를 통해 game log를 가져옴
        # game log를 저장
        # game을 update