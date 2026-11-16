from elasticsearch import Elasticsearch

# connexion à Elasticsearch
es = Elasticsearch("http://localhost:9200")

index_name = "smart_city_mobility"

# supprimer si l’index existe déjà
es.indices.delete(index=index_name, ignore=[400, 404])

# création de l’index + mapping
MAPPING = {
    "mappings": {
        "properties": {
            "trip_id":          {"type": "keyword"},
            "timestamp":        {"type": "date"},
            "hour":             {"type": "integer"},
            "day_of_week":      {"type": "keyword"},
            "month":            {"type": "integer"},
 
            "departure_zone":   {"type": "keyword"},
            "arrival_zone":     {"type": "keyword"},
            "departure_type":   {"type": "keyword"},
            "arrival_type":     {"type": "keyword"},
            "departure_coords": {"type": "geo_point"},
            "arrival_coords":   {"type": "geo_point"},
 
            "vehicle_type":     {"type": "keyword"},
            "distance_km":      {"type": "float"},
            "duration_min":     {"type": "integer"},
            "avg_speed_kmh":    {"type": "float"},
 
            "congestion_level": {"type": "keyword"},
            "weather":          {"type": "keyword"},
            "purpose":          {"type": "keyword"},
        }
    },
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0
    }
}

es.indices.create(index=index_name, body=MAPPING)

print(" Index créé :", index_name)

