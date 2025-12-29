from spade import agent

class HomeManagerAgent(agent.Agent):
    def __init__(self, jid, password, config, *args, **kwargs):
        super().__init__(jid, password, *args, **kwargs)
        self.config = config

    async def setup(self):
        print(f"[HomeManager] started as {self.jid}")
