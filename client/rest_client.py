import requests

class RestClient:
    def __init__(self, base_url="http://127.0.0.1:5000"):
        self.base_url = base_url

    def get_tables(self):
        response = requests.get(f"{self.base_url}/tables")
        return response.json() if response.status_code == 200 else None

    def create_table(self, table_name, fields):
        data = {"table_name": table_name, "fields": fields}
        response = requests.post(f"{self.base_url}/create_table", json=data)
        return response.json() if response.status_code == 200 else None

    def delete_table(self, table_name):
        response = requests.delete(f"{self.base_url}/delete_table/{table_name}")
        return response.json() if response.status_code == 200 else None
