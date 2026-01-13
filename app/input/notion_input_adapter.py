from notion_client import Client
import os

from input.input_adapter import InputAdapter

class NotionInputAdapter(InputAdapter):
    name: str = "Notion"
    database_id: str
    notion: Client

    def __init__(self, database_id: str):
        self.database_id = database_id

    def get_identifier(self) -> str:
        return self.name + "_" + self.database_id

    def read(self) -> dict:
        token = os.getenv("NOTION_TOKEN")
        if not token:
            raise ValueError("NOTION_TOKEN environment variable is not set")
        self.notion = Client(auth=token)
        print(self.notion.users.me())
        
        database = self.notion.databases.retrieve(
            **{
                "database_id": self.database_id,
            }
        )
        print(database)

        data_source_id = database["data_sources"][0]["id"]
        print(data_source_id)

        database = self.notion.data_sources.query(
            **{
                "data_source_id": data_source_id,
            }
        )
        print(database)

        return {"data": database}

def notion_property_to_value(prop: dict):
    prop_type = prop["type"]

    if prop_type == "title":
        return "".join(t["plain_text"] for t in prop["title"])

    if prop_type == "rich_text":
        return "".join(t["plain_text"] for t in prop["rich_text"])

    if prop_type == "number":
        return prop["number"]

    if prop_type == "select":
        return prop["select"]["name"] if prop["select"] else None

    if prop_type == "multi_select":
        return [v["name"] for v in prop["multi_select"]]

    if prop_type == "checkbox":
        return prop["checkbox"]

    if prop_type == "date":
        return prop["date"]["start"] if prop["date"] else None

    if prop_type == "relation":
        return [r["id"] for r in prop["relation"]]

    if prop_type == "url":
        return prop["url"]

    if prop_type == "email":
        return prop["email"]

    if prop_type == "phone_number":
        return prop["phone_number"]

    if prop_type == "people":
        return [p.get("name") for p in prop["people"]]

    # fallback (files, rollups, formulas, etc.)
    return None
