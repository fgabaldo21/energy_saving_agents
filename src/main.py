import yaml
import asyncio
from smart_home.device_agent import DeviceAgent
from smart_home.home_manager import HomeManagerAgent

with open('src/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    
async def main():
    home_manager_jid = config['xmpp']['manager']['jid']
    home_manager_password = config['xmpp']['manager']['password']
    home_manager_agent = HomeManagerAgent(home_manager_jid, home_manager_password, config)
    await home_manager_agent.start()

    device_agents = []
    for device in config['xmpp']['devices']:
        device_jid = device['jid']
        device_password = device['password']
        device_agent = DeviceAgent(device_jid, device_password, device, config)
        await device_agent.start()
        device_agents.append(device_agent)

    try:
        while home_manager_agent.is_alive():
            await asyncio.sleep(1)
        
        print("Home Manager has stopped. Shutting down device agents...")
    except KeyboardInterrupt:
        print("Stopping agents...")
    finally:
        await home_manager_agent.stop()
        for agent in device_agents:
            await agent.stop()
            
if __name__ == "__main__":
    asyncio.run(main())