from download import load_config,parallel_download_routing

feature_name = "environnement"
data_url = load_config()
parallel_download_routing(data_url[feature_name], feature_name)