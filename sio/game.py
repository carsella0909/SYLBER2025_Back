from socketio import AsyncNamespace


class GameNamespace(AsyncNamespace):
    async def on_connect(self):
        print("Client connected to the game namespace")

    async def on_disconnect(self):
        print("Client disconnected from the game namespace")

    async def on_message(self, data):
        print(f"Received message: {data}")
        await self.emit("response", {"data": "Message received!"})
