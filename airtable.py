import requests
from config import (
    GOOGLE_CLIENT_ID,
    GOOGLE_CLIENT_SECRET,
    AIRTABLE_API_KEY,
    AIRTABLE_BASE_ID,
    AIRTABLE_BASE_ID_2,
    AIRTABLE_CAPTIONS_TABLE,
    AIRTABLE_ACTIVE_CAPTIONS_VIEW,
    AIRTABLE_REELS_BABE_PAGE_TEMPLATE_VIEW,
    AIRTABLE_REELS_TABLE
)

# obj oriented approach for consolidating these fetch functions
class AirtableClient:
    def __init__(self, base_id, api_key):
        self.base_id = base_id
        self.api_key = api_key
        self.headers = {"Authorization": f"Bearer {self.api_key}"}

    def fetch_records(self, table_name, view_name=None):
        # Construct the endpoint with or without the view parameter
        if view_name:
            endpoint = f"https://api.airtable.com/v0/{self.base_id}/{table_name}?view={view_name}"
        else:
            endpoint = f"https://api.airtable.com/v0/{self.base_id}/{table_name}"

        all_records = []
        offset = None

        while True:
            params = {}
            if offset:
                params['offset'] = offset
            response = requests.get(endpoint, headers=self.headers, params=params)
            data = response.json()
            all_records.extend(data['records'])

            if 'offset' in data:
                offset = data['offset']
            else:
                break

        return all_records

    def update_record(self, table_name, record_id, fields):
        url = f"https://api.airtable.com/v0/{self.base_id}/{table_name}/{record_id}"
        data = {"fields": fields}
        response = requests.patch(url, headers=self.headers, json=data)

        if response.status_code != 200:
            raise Exception(f"Failed to update Airtable record: {response.status_code}, {response.text}")

        return response.json()