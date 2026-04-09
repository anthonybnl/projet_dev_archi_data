from download import load_config,parallel_download_routing, chemin

config = load_config()
#print(chemin())
for section in config.keys():
    # config[section] récupère le sous-dictionnaire d'URLs
    parallel_download_routing(config[section], section)