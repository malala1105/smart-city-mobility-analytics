from elasticsearch import Elasticsearch, helpers
import random
from datetime import datetime, timedelta
import uuid

# CONNEXION ELASTICSEARCH
es = Elasticsearch("http://localhost:9200")
index_name = "smart_city_mobility"

# ZONES D'ANTANANARIVO avec coordonnées GPS réelles
ZONES = {
    # --- Résidentiel ---
    "67Ha":            {"type": "residential", "lat": -18.9100, "lon": 47.5220},
    "Ivandry":         {"type": "residential", "lat": -18.8780, "lon": 47.5320},
    "Ambohijatovo":    {"type": "residential", "lat": -18.9150, "lon": 47.5330},
    "Faravohitra":     {"type": "residential", "lat": -18.9020, "lon": 47.5310},
    "Ambanidia":       {"type": "residential", "lat": -18.9200, "lon": 47.5290},
    "Ankadifotsy":     {"type": "residential", "lat": -18.9350, "lon": 47.5260},
    "Itaosy":          {"type": "residential", "lat": -18.9550, "lon": 47.5000},

    # --- Commercial / Business ---
    "Analakely":       {"type": "business",    "lat": -18.9137, "lon": 47.5361},
    "Ankorondrano":    {"type": "business",    "lat": -18.8950, "lon": 47.5280},
    "Andraharo":       {"type": "business",    "lat": -18.8870, "lon": 47.5210},
    "Tsaralalàna":     {"type": "business",    "lat": -18.9080, "lon": 47.5340},
    "Isotry":          {"type": "business",    "lat": -18.9180, "lon": 47.5240},
    "Tanjombato":      {"type": "business",    "lat": -18.9700, "lon": 47.5250},

    # --- Éducation ---
    "Ankatso":         {"type": "education",   "lat": -18.9100, "lon": 47.5440},
    "Mahamasina":      {"type": "education",   "lat": -18.9230, "lon": 47.5380},

    # --- Transport hub ---
    "Ambohidahy":      {"type": "transport",   "lat": -18.9060, "lon": 47.5370},
    "Anosibe":         {"type": "transport",   "lat": -18.9300, "lon": 47.5200},
}

# DISTANCES RÉELLES
def haversine_km(lat1, lon1, lat2, lon2):
    """Distance à vol d'oiseau en km."""
    import math
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon/2)**2
    return R * 2 * math.asin(math.sqrt(a))

def road_distance_km(zone_a, zone_b):
    """Distance routière : vol d'oiseau × 1.4 (sinuosité routes de Tana) ± 10%."""
    za = ZONES[zone_a]
    zb = ZONES[zone_b]
    d_air = haversine_km(za["lat"], za["lon"], zb["lat"], zb["lon"])
    return round(max(0.5, d_air * 1.4 * random.uniform(0.90, 1.10)), 2)

# VÉHICULES avec profils réalistes
VEHICLE_PROFILES = {
    "car": {
        # Véhicule le plus répandu à Tana — présent toute la journée
        "speed_kmh":    {"low": 35, "medium": 25, "high": 14},
        "min_distance": 1.0,
        "hours_weights": [0,0,0,0,0,2,5,8,7,5,5,5,5,5,5,5,5,8,7,4,3,2,0,0],
    },
    "taxi": {
        # Minoritaire — quelques courses en journée et soirée
        "speed_kmh":    {"low": 30, "medium": 22, "high": 12},
        "min_distance": 0.8,
        "hours_weights": [0,0,0,0,0,1,2,3,3,2,2,2,2,2,2,2,2,3,3,2,1,1,0,0],
    },
    "moto": {
        # Assez présent, surtout heures de pointe et journée
        "speed_kmh":    {"low": 38, "medium": 28, "high": 16},
        "min_distance": 0.5,
        "hours_weights": [0,0,0,0,0,1,3,5,5,4,4,4,4,4,4,4,4,5,5,3,2,1,0,0],
    },
    "taxi-be": {
        # Transport en commun dominant — très chargé aux heures de pointe
        "speed_kmh":    {"low": 20, "medium": 14, "high": 8},
        "min_distance": 1.5,
        "hours_weights": [0,0,0,0,0,3,6,8,7,5,5,5,5,5,5,5,6,8,7,4,2,1,0,0],
    },
}

# MÉTÉO saisonnière (saison des pluies nov–avril)
def get_weather(month):
    rainy_months = {11: 0.45, 12: 0.55, 1: 0.60, 2: 0.65, 3: 0.55, 4: 0.40}
    p_rain = rainy_months.get(month, 0.10)
    return random.choices(["sunny", "rain", "cloudy"], weights=[1 - p_rain - 0.1, p_rain, 0.1])[0]

# CONGESTION selon heure ET météo
def get_congestion(hour, weather):
    if 6 <= hour <= 9 or 16 <= hour <= 19:
        level = "high"
    elif 10 <= hour <= 15:
        level = "medium"
    else:
        level = "low"
    if weather == "rain" and level == "medium":
        level = "high"
    elif weather == "rain" and level == "low":
        level = "medium"
    return level

# LOGIQUE DÉPART / ARRIVÉE
def get_zones_by_type(zone_type):
    return [z for z, v in ZONES.items() if v["type"] == zone_type]

residential_zones = get_zones_by_type("residential")
business_zones    = get_zones_by_type("business")
education_zones   = get_zones_by_type("education")
transport_zones   = get_zones_by_type("transport")
all_zones         = list(ZONES.keys())

def get_trip(hour):
    r = random.random()
    if 6 <= hour <= 9:
        if r < 0.55:
            return random.choice(residential_zones), random.choice(business_zones), "work"
        elif r < 0.80:
            return random.choice(residential_zones), random.choice(education_zones), "study"
        else:
            dep = random.choice(all_zones)
            return dep, random.choice([z for z in all_zones if z != dep]), "other"
    elif 10 <= hour <= 15:
        if r < 0.35:
            dep = random.choice(business_zones + transport_zones)
            return dep, random.choice([z for z in business_zones + transport_zones if z != dep]), "work"
        elif r < 0.55:
            return random.choice(business_zones), random.choice(residential_zones), "leisure"
        else:
            dep = random.choice(all_zones)
            return dep, random.choice([z for z in all_zones if z != dep]), "leisure"
    elif 16 <= hour <= 19:
        if r < 0.60:
            return random.choice(business_zones), random.choice(residential_zones), "work"
        elif r < 0.75:
            return random.choice(education_zones), random.choice(residential_zones), "study"
        else:
            dep = random.choice(all_zones)
            return dep, random.choice([z for z in all_zones if z != dep]), "leisure"
    else:
        dep = random.choice(all_zones)
        purpose = random.choices(["leisure", "work", "other"], weights=[0.6, 0.2, 0.2])[0]
        return dep, random.choice([z for z in all_zones if z != dep]), purpose

# CALCUL DURÉE
def compute_duration(distance_km, vehicle, congestion, weather):
    speed = VEHICLE_PROFILES[vehicle]["speed_kmh"][congestion]
    if weather == "rain":
        speed *= 0.85
    return max(3, int((distance_km / speed) * 60 * random.uniform(0.92, 1.08)))

# GÉNÉRATION D'UN DOCUMENT
def generate_doc(base_date):
    hour = random.choices(range(5, 23), weights=[
        1, 3, 5, 4, 2, 2, 2, 2, 2, 2, 2, 3, 5, 4, 2, 1, 1, 1
    ])[0]

    departure, arrival, purpose = get_trip(hour)
    day     = base_date - timedelta(days=random.randint(0, 29))
    month   = day.month
    weather = get_weather(month)
    congestion = get_congestion(hour, weather)

    vehicle_weights = {v: VEHICLE_PROFILES[v]["hours_weights"][hour] for v in VEHICLE_PROFILES}
    if sum(vehicle_weights.values()) == 0:
        vehicle = random.choice(list(vehicle_weights.keys()))
    else:
        vehicle = random.choices(list(vehicle_weights.keys()), weights=list(vehicle_weights.values()))[0]

    distance_km = road_distance_km(departure, arrival)
    if distance_km < VEHICLE_PROFILES[vehicle]["min_distance"]:
        vehicle = random.choice(["moto", "taxi"])

    duration_min = compute_duration(distance_km, vehicle, congestion, weather)
    avg_speed    = round((distance_km / duration_min * 60), 1) if duration_min > 0 else 0

    timestamp = day.replace(
        hour=hour,
        minute=random.randint(0, 59),
        second=random.randint(0, 59),
        microsecond=0
    )

    return {
        "_index": index_name,
        "_id": str(uuid.uuid4()),
        "_source": {
            "trip_id":          str(uuid.uuid4()),
            "timestamp":        timestamp.isoformat(),
            "hour":             hour,
            "day_of_week":      timestamp.strftime("%A"),
            "month":            month,

            "departure_zone":   departure,
            "arrival_zone":     arrival,
            "departure_type":   ZONES[departure]["type"],
            "arrival_type":     ZONES[arrival]["type"],
            "departure_coords": {"lat": ZONES[departure]["lat"], "lon": ZONES[departure]["lon"]},
            "arrival_coords":   {"lat": ZONES[arrival]["lat"],   "lon": ZONES[arrival]["lon"]},

            "vehicle_type":     vehicle,
            "distance_km":      distance_km,
            "duration_min":     duration_min,
            "avg_speed_kmh":    avg_speed,

            "congestion_level": congestion,
            "weather":          weather,
            "purpose":          purpose,
        }
    }

# GÉNÉRATION ET INSERTION
if __name__ == "__main__":
    import csv
    from collections import Counter

    base_date = datetime.now()
    N = 10_000

    print(f"⏳ Génération de {N:,} documents...")
    docs = [generate_doc(base_date) for _ in range(N)]

    # Insertion Elasticsearch
    helpers.bulk(es, docs, chunk_size=500, request_timeout=60)
    print(f"✅ {N:,} documents insérés dans '{index_name}'.")

    # Export CSV (version offline)
    CSV_FILE = "mobility_tana.csv"
    CSV_FIELDS = [
        "trip_id", "timestamp", "hour", "day_of_week", "month",
        "departure_zone", "arrival_zone", "departure_type", "arrival_type",
        "departure_lat", "departure_lon", "arrival_lat", "arrival_lon",
        "vehicle_type", "distance_km", "duration_min", "avg_speed_kmh",
        "congestion_level", "weather", "purpose",
    ]
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for doc in docs:
            s = doc["_source"]
            writer.writerow({
                "trip_id":          s["trip_id"],
                "timestamp":        s["timestamp"],
                "hour":             s["hour"],
                "day_of_week":      s["day_of_week"],
                "month":            s["month"],
                "departure_zone":   s["departure_zone"],
                "arrival_zone":     s["arrival_zone"],
                "departure_type":   s["departure_type"],
                "arrival_type":     s["arrival_type"],
                "departure_lat":    s["departure_coords"]["lat"],
                "departure_lon":    s["departure_coords"]["lon"],
                "arrival_lat":      s["arrival_coords"]["lat"],
                "arrival_lon":      s["arrival_coords"]["lon"],
                "vehicle_type":     s["vehicle_type"],
                "distance_km":      s["distance_km"],
                "duration_min":     s["duration_min"],
                "avg_speed_kmh":    s["avg_speed_kmh"],
                "congestion_level": s["congestion_level"],
                "weather":          s["weather"],
                "purpose":          s["purpose"],
            })
    print(f" Dataset exporté → {CSV_FILE}")

    # Statistiques rapides
    vehicles  = Counter(d["_source"]["vehicle_type"]     for d in docs)
    weathers  = Counter(d["_source"]["weather"]          for d in docs)
    congest   = Counter(d["_source"]["congestion_level"] for d in docs)
    purposes  = Counter(d["_source"]["purpose"]          for d in docs)
    distances = [d["_source"]["distance_km"]             for d in docs]

    print("\n Statistiques du dataset :")
    print(f"  Véhicules    : {dict(vehicles)}")
    print(f"  Météo        : {dict(weathers)}")
    print(f"  Congestion   : {dict(congest)}")
    print(f"  Motifs       : {dict(purposes)}")
    print(f"  Distance moy : {sum(distances)/len(distances):.2f} km")
    print(f"  Distance min : {min(distances):.2f} km")
    print(f"  Distance max : {max(distances):.2f} km")