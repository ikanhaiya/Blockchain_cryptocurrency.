

import asyncio
from textwrap import dedent


class ConnectionPool:
    def __init__(self):
        self.connection_pool=set()

    def send_welcome_message(self,writer):
        """Sends welcome message to newly connected user"""
        message = dedent(f"""Welcome {writer.nickname}! There are {len(self.connection_pool)-1} users here with you.
        Guidlines:
            -> Type anything to chat
            -> /list will list all the connected users 
            -> /quit will disconnect you""")

        writer.write(f"{message}\n".encode())

    def broadcast(self, writer, message):
        # broadcast general notification to entire connection or pool

        for user in self.connection_pool:
            if user!=writer:
                user.write(f"{message}\n".encode())
        

    def broadcast_user_join(self,writer):

        self.broadcast(writer, f"{writer.nickname} joined chat group.")
        # calls broadcast method with user joining message
        

    def broadcast_user_quit(self,writer):
        # calls broadcast method with user quitting message
        self.broadcast(writer, f"{writer.nickname} left chat group.")
        

    def broadcast_new_message(self, writer, message):
        # calls broadcast message with user's chat message
        self.broadcast(writer, f"[{writer.nickname}] {message}")

    def list_users(self,writer):
        # list all the users in the network
        message = "===\n"
        message += "Currently connected users: "
        for user in self.connection_pool:
            if user==writer:
                message += f"\n - {user.nickname} (you)"
            else:
                message += f"\n - {user.nickname}"

        message += "\n==="
        writer.write(f"{message}\n".encode())
        

    def add_new_user_to_pool(self,writer):
        # Adds new user to our existing pool
        self.connection_pool.add(writer)

    def remove_user_from_pool(self, writer):
        # Removes existing user from pool
        self.connection_pool.remove(writer)




async def handle_connection(reader, writer):  #implicitly receives reader and writer as an arguments
  

    #get a nickname for the new client  page : 70
    writer.write("> Choose your nickname: ".encode())

    response = await reader.readuntil(b"\n")
    writer.nickname = response.decode().strip()

    connection_pool.add_new_user_to_pool(writer)
    connection_pool.send_welcome_message(writer)

   # await writer.drain()

   #Announce the arrival of this new user 
    connection_pool.broadcast_user_join(writer)

    while True:
        try:
            data=await reader.readuntil(b"\n")
        except asyncio.exceptions.IncompleteReadError:
            connection_pool.broadcast_user_quit(writer)
            break
        message = data.decode().strip()
        if message == "/quit":
            connection_pool.broadcast_user_quit(writer)
            break

        elif message=="/list":
            connection_pool.list_users(writer)
        else:
            connection_pool.broadcast_new_message(writer,message)
        
        await writer.drain()

        if writer.is_closing():
            break


        

    # we are now outside msg loop and user has quit. Close the connection and clean up
    writer.close()
    await writer.wait_closed()
    connection_pool.remove_user_from_pool(writer)



async def main():
    server = await asyncio.start_server(handle_connection, "0.0.0.0", 8888) # server is inatialized with callback function ,
    # handle connection to handle new connection....

    async with server:
        await server.serve_forever()

connection_pool = ConnectionPool()
 
asyncio.run(main())
