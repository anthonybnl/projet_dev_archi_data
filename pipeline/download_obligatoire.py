from download import load_config,parallel_download_routing

feature_name = "obligatoire"
data_url = load_config()
feature_data = data_url[feature_name]
parallel_download_routing(feature_data.values(), feature_name)