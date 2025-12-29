from spade import agent

class DeviceAgent(agent.Agent):
    def __init__(self, jid, password, device_config, global_config, *args, **kwargs):
        super().__init__(jid, password, *args, **kwargs)
        self.device_config = device_config
        self.global_config = global_config

    async def setup(self):
        print(f"[Device] {self.device_config['name']} started as {self.jid}")