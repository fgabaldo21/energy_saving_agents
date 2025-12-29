from spade import agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
import json

class HomeManagerAgent(agent.Agent):
    def __init__(self, jid, password, config, *args, **kwargs):
        super().__init__(jid, password, *args, **kwargs)
        self.config = config
        self.current_load = 0.0
        self.max_load = config['simulation']['max_power_kw']

    async def setup(self):
        print(f"[HomeManager] started as {self.jid}. Max load: {self.max_load} kW")
        b = self.EnergyManagerBehaviour()
        self.add_behaviour(b)
        
    class EnergyManagerBehaviour(CyclicBehaviour):
        async def run(self):
            msg = await self.receive(timeout=10)
            
            if msg:
                content = json.loads(msg.body)
                device_power = content.get('power_kw', 0.0)
                performative = content
                
            if performative == 'REQUEST':
                print(f"[HomeManager] Received REQUEST for {device_power} kW from {msg.sender}")
                
                reply = msg.make_reply()
                
                if self.agent.current_load + device_power <= self.agent.max_load:
                    self.agent.current_load += device_power
                    reply.body = json.dumps({'status': 'APPROVED', "current_total": self.agent.current_load})
                    print(f"[HomeManager] Approved request from {msg.sender}. Current load: {self.agent.current_load} kW")
                    
                else:
                    reply.set_metadata("performative", "REFUSE")
                    reply.body = json.dumps({"status": "denied", "reason": "overload"})
                    print(f"[HomeManager] Denied request from {msg.sender}. Would exceed max load.")
                    
                await self.send(reply)
                
            elif performative == 'INFORM' and content.get('status') == "finished":
                self.agent.current_load -= device_power
                print(f"[HomeManager] Device {msg.sender} finished. Current load: {self.agent.current_load} kW")
                
            else:
                await self.agent.sleep(1)
                pass
