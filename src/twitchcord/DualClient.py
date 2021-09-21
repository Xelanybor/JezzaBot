import asyncio

class dualClient:
    """A class that represents a dual Twitch/Discord client."""

    def __init__(self, discordClient, twitchClient, discordToken):
        self.discordClient = discordClient
        self.twitchClient = twitchClient
        # So that each bot can access the other in cog files.
        self.discordClient.twitchClient = twitchClient
        self.twitchClient.discordClient = discordClient
        self.discordToken = discordToken

    def run(self):
        "A blocking function that starts up both the discord and twitch clients."
        try:
            loop = asyncio.get_event_loop()
            loop.create_task(self.twitchClient.connect())
            loop.create_task(self.discordClient.start(self.discordToken))
            loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            loop.run_until_complete(self.twitchClient.close())
            loop.close()