import random
from spade.agent import Agent
from spade.behaviour import OneShotBehaviour, CyclicBehaviour
from spade.message import Message
import json
import asyncio

class DeviceAgent(Agent):
    def __init__(self, jid, password, device_config, global_config, *args, **kwargs):
        super().__init__(jid, password, *args, **kwargs)
        self.device_config = device_config
        self.manager_jid = global_config['xmpp']['manager']['jid']

    async def setup(self):
        print(f"[Device] {self.device_config['name']} is ready.")
        
        initial_wait = random.uniform(1, 5)
        await asyncio.sleep(initial_wait)
        
        self.add_behaviour(self.NegotiationBehaviour())

    class NegotiationBehaviour(OneShotBehaviour):
        async def run(self):
            print(f"[Device] {self.agent.device_config['name']} is sending request to work...")
            
            msg = Message(to=self.agent.manager_jid)
            msg.set_metadata("performative", "REQUEST")
            msg.body = json.dumps({
                "power": self.agent.device_config['power_kw'],
                "duration": self.agent.device_config['duration_minutes']
            })
            await self.send(msg)

            reply = await self.receive(timeout=10)
            
            if reply:
                perf = reply.get_metadata("performative")
                if perf == "APPROVED":
                    print(f"[Device] {self.agent.device_config['name']} recieved approval to work. Starting work...")
                    self.agent.add_behaviour(self.agent.WorkBehaviour())
                else:
                    wait_time = random.uniform(3, 7)
                    print(f"[Device] {self.agent.device_config['name']} was rejected. Will try again in {wait_time} seconds...")
                    await asyncio.sleep(wait_time)
                    self.agent.add_behaviour(self.agent.NegotiationBehaviour())
            else:
                print(f"[Device] {self.agent.device_config['name']} did not receive a response from the Manager.")
                
    class WorkBehaviour(OneShotBehaviour):
        async def run(self):
            duration = self.agent.device_config['duration_minutes']
            real_seconds = duration / self.agent.global_config['simulation']['tick_duration']
            print(f"[Device] {self.agent.device_config['name']} is working... (duration: {duration}h)")
            
            await asyncio.sleep(real_seconds)
            
            print(f"[Device] {self.agent.device_config['name']} has finished working.")
            
            msg = Message(to=self.agent.manager_jid)
            msg.set_metadata("performative", "INFORM")
            msg.body = json.dumps({
                "status": "finished",
                "power": self.agent.device_config['power_kw']
            })
            await self.send(msg)