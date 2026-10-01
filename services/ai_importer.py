import requests

AI_API = "http://127.0.0.1:8000/publish"


def import_from_ai(product):

    response = requests.post(
        AI_API,
        json=product
    )

    print("Status Code:", response.status_code)
    print("Response:", response.text)

    response.raise_for_status()

    return response.json()