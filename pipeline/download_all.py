from download import load_config,parallel_download_routing

config = load_config()

for section in config.keys():
    # config[section] récupère le sous-dictionnaire d'URLs
    parallel_download_routing(config[section], section)