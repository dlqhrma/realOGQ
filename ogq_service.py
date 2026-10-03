import os
import requests

BASE_URL = "https://4th-ai-ogq.competition.ogq.me"

def search_assets(query):
    headers = {
        "X-OGQ-API-KEY": os.getenv("OGQ_API_KEY")
    }

    response = requests.get(
        f"{BASE_URL}/v1/assets",
        headers=headers,
        params={
            "query": query,
            "pageSize": 10
        },
        timeout=10
    )

    response.raise_for_status()
    return response.json()