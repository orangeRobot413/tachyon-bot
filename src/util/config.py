import json


# MARK: Config
class Config:

    def __init__(self, filename: str):
        '''
        Initialize a `Config` object from a json file
        
        :param str filename: The config json file to load
        '''

        file = open(filename)
        data = json.load(file)

        # Initialize from data
        self.discord_token = str(data['discord_token'])
        '''The discord bot's token'''

        self.server_name = str(data['server_name'])
        '''The collective server/community name'''

        self.roles = Config.Roles(**data['roles'])
        '''The IDs of specific Discord roles'''

        self.servers = {
            str(server): Config.Server(**data['servers'][server])
            for server in data['servers']
        }
        '''All associated minecraft servers'''

        file.close()

    class Roles:
        '''Specific Discord role IDs'''

        def __init__(self, *, admin: int, mod: int, member: int,
                     provisional: int, **kwargs):
            '''
            Initialize a `Roles` object.

            :param int admin: The ID of the Discord admin role
            :param int member: The ID of the Discord member role
            :param int provisional: The ID of the Discord provisional role
            '''

            self.admin = int(admin)
            self.mod = int(mod)
            self.member = int(member)
            self.provisional = int(provisional)

    class Server:
        '''The metadata for a minecraft server'''

        def __init__(self, *, name: str, path: str, server_jar: str, rcon_port: int, rcon_pass: str, ram: int,
                     **kwargs):
            '''
            Initialize a `Server` object.

            :param str name: The full capitalized name of the server
            :param str path: The path to the servers root directory
            :param int ram: The RAM to be alloted to the server in MB
            '''

            self.name = str(name)
            '''The server's display name'''

            self.path = str(path)
            '''The server's root directory'''

            self.server_jar = str(server_jar)
            '''The filename of the server jar'''

            self.rcon = Config.Server.Rcon(port=int(rcon_port), password=str(rcon_pass))
            '''The server's RCON configuration'''

            self.ram = str(ram)
            '''The amount of RAM in MB to allocate'''

        class Rcon:
            '''The server's RCON configuration'''

            def __init__(self, *, port: int, password: str):
                '''
                Initialize a `Rcon` object.

                :param int port: The RCON port
                :param str password: The RCON password
                '''

                self.port = int(port)
                '''The server's RCON port'''

                self.password = str(password)
                '''The server's RCON password'''
