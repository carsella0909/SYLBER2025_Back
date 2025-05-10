from socketio import AsyncNamespace


class GameNamespace(AsyncNamespace):
    def on_disconnect(self, sid, reason):
        print("Client disconnected from the game namespace")

    async def on_message(self, sid, data):
        print(f"Received message: {data}")
        await self.emit('my_response', data)
