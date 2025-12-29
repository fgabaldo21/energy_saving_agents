import yaml

with open('src/config.yaml', 'r') as file:
    config = yaml.safe_load(file)
    
print(config['xmpp']['devices'])