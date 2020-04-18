#
# Серверное приложение для соединений
#
import asyncio
from asyncio import transports


class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport

    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):
        decoded = data.decode(encoding="utf-8", errors="ignore")

        if self.login is not None:
            self.send_message(decoded.replace("\r\n", ""))
        else:
            if decoded.startswith("login:"):
                self.login = decoded.replace("login:", "").replace("\r\n", "")
                for user in self.server.clients:
                    if user.login == self.login and user != self:
                        self.transport.write(
                            f"Логин {self.login}  занят, попробуйте другой".encode(encoding="utf-8", errors="ignore")
                        )
                        #Login <{self.login}> is busy, try another one...
                        self.transport.close()
                self.transport.write(
                     f"Hello, {self.login}!\n".encode(encoding="utf-8", errors="ignore")
                )
                self.send_history()

            else:
                self.transport.write("Command format for the firs message login:LOGIN\n".
                                     encode(encoding="utf=8", errors="ignore"))


    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("Пришел новый клиент")

    def connection_lost(self, exception):
        self.server.clients.remove(self)
        print("Клиент вышел")

    def send_message(self, content: str):
        message = f"{self.login}: {content}"

        self.write_history(massage)

        for user in self.server.clients:
            user.transport.write(message.encode(encoding="utf=8", errors="ignore"))

    def send_history(self):
        if len(self.server.history) > 0:
            self.transport.write(f"Last massages >>\n{''.join(self.server.history)}".
                                 encode(encoding="utf=8", errors="ignore"))


    def write_history(self, massage: str):
        if len(self.server.history) < 10:
            self.server.history.append(massage)
        else:
            self.server.history.append(massage)
            self.server.history.pop(0)






class Server:
    clients: list
    history: list

    def __init__(self):
        self.history = []
        self.clients = []


    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()


process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")
    sys.exit(0)