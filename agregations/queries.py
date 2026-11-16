from elasticsearch import Elasticsearch

es = Elasticsearch("http://localhost:9200")
INDEX = "smart_city_mobility"


# construit le filtre "query" selon les paramètres
def _build_filter(vehicule=None, meteo=None, heure_min=None, heure_max=None):
    """
    Retourne un bloc 'query' Elasticsearch à injecter dans les agrégations.
    Si aucun filtre → match_all (comportement identique à avant).
    """
    filters = []

    if vehicule and vehicule != "Tous":
        filters.append({"term": {"vehicle_type": vehicule}})
    if meteo and meteo != "Tous":
        filters.append({"term": {"weather": meteo}})
    if heure_min is not None and heure_max is not None:
        filters.append({"range": {"hour": {"gte": heure_min, "lte": heure_max}}})

    if not filters:
        return {"match_all": {}}
    return {"bool": {"filter": filters}}


# 1. TRAFIC PAR HEURE
def trafic_par_heure(vehicule=None, meteo=None):
    resp = es.search(index=INDEX, body={
        "size": 0,
        "query": _build_filter(vehicule=vehicule, meteo=meteo),
        "aggs": {
            "par_heure": {
                "terms": {"field": "hour", "size": 24, "order": {"_key": "asc"}}
            }
        }
    })
    buckets = resp["aggregations"]["par_heure"]["buckets"]
    return {b["key"]: b["doc_count"] for b in buckets}


# 2. ZONES LES PLUS CHARGÉES
def zones_plus_chargees(vehicule=None, meteo=None, top=7):
    resp = es.search(index=INDEX, body={
        "size": 0,
        "query": _build_filter(vehicule=vehicule, meteo=meteo),
        "aggs": {
            "top_departs":  {"terms": {"field": "departure_zone", "size": top}},
            "top_arrivees": {"terms": {"field": "arrival_zone",   "size": top}},
        }
    })
    aggs = resp["aggregations"]
    return {
        "departs":  {b["key"]: b["doc_count"] for b in aggs["top_departs"]["buckets"]},
        "arrivees": {b["key"]: b["doc_count"] for b in aggs["top_arrivees"]["buckets"]},
    }


# 3. IMPACT MÉTÉO
def impact_meteo(vehicule=None, heure_min=None, heure_max=None):
    resp = es.search(index=INDEX, body={
        "size": 0,
        "query": _build_filter(vehicule=vehicule, heure_min=heure_min, heure_max=heure_max),
        "aggs": {
            "par_meteo": {
                "terms": {"field": "weather"},
                "aggs": {
                    "duree_moyenne":    {"avg": {"field": "duration_min"}},
                    "distance_moyenne": {"avg": {"field": "distance_km"}},
                }
            }
        }
    })
    buckets = resp["aggregations"]["par_meteo"]["buckets"]
    return {
        b["key"]: {
            "duree_moyenne":    round(b["duree_moyenne"]["value"], 1),
            "distance_moyenne": round(b["distance_moyenne"]["value"], 2),
        }
        for b in buckets
    }


# 4. DISTANCE ET DURÉE MOYENNES PAR VÉHICULE
def stats_par_vehicule(meteo=None, heure_min=None, heure_max=None):
    resp = es.search(index=INDEX, body={
        "size": 0,
        "query": _build_filter(meteo=meteo, heure_min=heure_min, heure_max=heure_max),
        "aggs": {
            "par_vehicule": {
                "terms": {"field": "vehicle_type"},
                "aggs": {
                    "distance_moyenne": {"avg": {"field": "distance_km"}},
                    "duree_moyenne":    {"avg": {"field": "duration_min"}},
                    "vitesse_moyenne":  {"avg": {"field": "avg_speed_kmh"}},
                }
            }
        }
    })
    buckets = resp["aggregations"]["par_vehicule"]["buckets"]
    return {
        b["key"]: {
            "distance_moyenne": round(b["distance_moyenne"]["value"], 2),
            "duree_moyenne":    round(b["duree_moyenne"]["value"], 1),
            "vitesse_moyenne":  round(b["vitesse_moyenne"]["value"], 1),
            "nb_trajets":       b["doc_count"],
        }
        for b in buckets
    }

# 5. RÉPARTITION DES VÉHICULES PAR TYPE DE ZONE
def vehicules_par_type_zone():
    resp = es.search(index=INDEX, body={
        "size": 0,
        "aggs": {
            "par_type_zone": {
                "terms": {"field": "departure_type"},
                "aggs": {
                    "par_vehicule": {
                        "terms": {"field": "vehicle_type"}
                    }
                }
            }
        }
    })
    buckets = resp["aggregations"]["par_type_zone"]["buckets"]
    result = {}
    for b in buckets:
        zone_type = b["key"]
        result[zone_type] = {
            v["key"]: v["doc_count"]
            for v in b["par_vehicule"]["buckets"]
        }
    return result