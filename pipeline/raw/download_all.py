from download import load_config,parallel_download_routing

config = load_config()
#print(chemin())
for section in config.keys():
    parallel_download_routing(config[section], section)