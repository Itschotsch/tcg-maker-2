import ast
import os
import logging
import pandas as pd
import re

from notion2pandas import Notion2PandasClient

from input.input_adapter import InputAdapter

class NotionInputAdapter(InputAdapter):

    database_id: str

    def __init__(self, database_id: str):
        """
        Create the adapter, storing the Notion database ID.
        """
        self.database_id = database_id

    def get_identifier(self) -> str:
        return f"notion_input_adapter_{self.database_id}"

    def get_display_name(self) -> str:
        return f"Notion Import"

    async def read(self) -> pd.DataFrame:
        """
        Read all rows from the Notion database into a pandas DataFrame.
        Resolves Relation IDs to Titles only for specific columns to save API calls.
        """
        log = logging.getLogger(__name__)

        # Ensure the token is present
        token = os.getenv("NOTION_TOKEN")
        if not token:
            raise ValueError("NOTION_TOKEN environment variable is not set")

        log.info(f"Reading from Notion database with ID: {self.database_id}")

        # Initialise the notion2pandas client
        client: Notion2PandasClient
        try:
            client = Notion2PandasClient(auth=token)
            log.info("Successfully created Notion2PandasClient")
        except Exception as e:
            log.error(f"Failed to initialize Notion2PandasClient: {e}")
            raise

        # 1. Define columns that require name resolution
        # Use a set for faster lookup
        RESOLVE_TITLES_FOR = {'Kartenart', 'Kartentyp', 'Element'}

        # 2. Initialise cache
        page_title_cache = {}

        # 3. Define custom reader with 'column_name' argument
        # The library detects 'column_name' in the signature and injects it automatically.
        def cached_relation_read(notion_property: dict, column_name: str, n2p) -> str:
            relations = notion_property.get('relation', [])
            
            # --- OPTIMISATION CHECK ---
            # If this is NOT a target column, just return the IDs (Default behavior)
            # This saves API calls for columns you don't care about.
            if column_name not in RESOLVE_TITLES_FOR:
                return str([r.get('id') for r in relations])
            # --------------------------

            titles = []

            for item in relations:
                page_id = item.get('id')
                
                if page_id in page_title_cache:
                    titles.append(page_title_cache[page_id])
                    continue

                try:
                    page_data = n2p.retrieve_page(page_id)
                    
                    page_title = "Untitled"
                    for prop in page_data.get('properties', {}).values():
                        if prop.get('type') == 'title':
                            title_list = prop.get('title', [])
                            if title_list:
                                page_title = title_list[0].get('plain_text', '')
                            break
                    
                    page_title_cache[page_id] = page_title
                    titles.append(page_title)

                except Exception as e:
                    log.warning(f"Could not resolve relation {page_id} in column {column_name}: {e}")
                    titles.append(f"Error: {page_id}")
                    page_title_cache[page_id] = f"Error: {page_id}"

            return str(titles)

        # 4. Apply the override
        if 'relation' in client.switcher:
            original_write_func = client.switcher['relation'][1].function
            client.set_lambdas('relation', cached_relation_read, original_write_func)

        # Fetch Data
        try:
            log.debug("Fetching data from Notion...")
            df: pd.DataFrame = client.from_notion_DB_to_dataframe(self.database_id)
            log.info(f"Successfully loaded {len(df)} rows.")
            log.debug(f"Relation cache size: {len(page_title_cache)} unique pages resolved.")
        except Exception as e:
            log.error(f"Error fetching Notion DB: {e}")
            raise

        return sanitise_notion_dataframe(df)

def sanitise_notion_dataframe(df: pd.DataFrame) -> pd.DataFrame:

    print("Sanitising dataframe...")

    df = df.copy()
    df = df[[
        "ID",
        "Kartenart",
        "Kartentyp",
        "Name",
        "Kartentext",
        "Kartentext-Planung",
        "Flavourtext",
        "Kosten Terra",
        "Kosten Aqua",
        "Kosten Aeris",
        "Kosten Ignis",
        "Kosten Magica",
        "Kosten Ungeprägt",
        "Element",
        "⚔️",
        "🛡️",
        "⭕️",
    ]]

    # ID

    # Kind
    df = df.rename(columns={"Kartenart": "kind"})
    print("Kind before:", df["kind"].unique())
    df["kind"] = df["kind"].apply(sanitise_relation_name)
    print("Kind after:", df["kind"].unique())

    # Type
    df = df.rename(columns={"Kartentyp": "type"})
    print("Type before:", df["type"].unique())
    df["type"] = df["type"].apply(sanitise_relation_name)
    print("Type after:", df["type"].unique())

    # Title
    df[["title_primary", "title_secondary"]] = df["Name"].str.split(",", n=1, expand=True)
    df = df.drop(columns=["Name"])

    # Description
    df["description"] = df.apply(lambda row: row["Kartentext"] if pd.notna(row["Kartentext"]) else row["Kartentext-Planung"], axis=1)
    df = df.drop(columns=["Kartentext", "Kartentext-Planung"])

    # Flavour
    df["flavour"] = df["Flavourtext"]
    df = df.drop(columns=["Flavourtext"])

    # Cost
    df = df.rename(columns={"Kosten Terra": "cost_terra"})
    df = df.rename(columns={"Kosten Aqua": "cost_aqua"})
    df = df.rename(columns={"Kosten Aeris": "cost_aeris"})
    df = df.rename(columns={"Kosten Ignis": "cost_ignis"})
    df = df.rename(columns={"Kosten Magica": "cost_magica"})
    df = df.rename(columns={"Kosten Ungeprägt": "cost_unshaped"})

    # Elemental Element
    df = df.rename(columns={"Element": "elemental_element"})
    print("Elemental Element before:", df["elemental_element"].unique())
    df["elemental_element"] = df["elemental_element"].apply(sanitise_relation_name)
    print("Elemental Element after:", df["elemental_element"].unique())

    # Elemental Amount
    df["elemental_amount"] = 1

    # Stats Offensive
    df[["stats_offensive_strength", "stats_offensive_toughness"]] = df["⚔️"].str.split("/", n=1, expand=True)
    df["stats_offensive_strength"] = df["stats_offensive_strength"].replace("-", None)
    df["stats_offensive_toughness"] = df["stats_offensive_toughness"].replace("-", None)
    df = df.drop(columns=["⚔️"])

    # Stats Defensive
    df[["stats_defensive_strength", "stats_defensive_toughness"]] = df["🛡️"].str.split("/", n=1, expand=True)
    df["stats_defensive_strength"] = df["stats_defensive_strength"].replace("-", None)
    df["stats_defensive_toughness"] = df["stats_defensive_toughness"].replace("-", None)
    df = df.drop(columns=["🛡️"])

    # Stats Barriers
    df["stats_barriers"] = df["⭕️"].replace("-", None)
    df = df.drop(columns=["⭕️"])

    print("Sanitised dataframe.")

    return df

def sanitise_relation_name(name: str | None) -> str | None:
    if pd.isna(name) or str(name).strip() == "" or str(name).strip() == "[]":
        return None

    name = str(name)

    # Case: "['Foo Bar']" -> "Foo Bar"
    if name.startswith("[") and name.endswith("]"):
        try:
            parsed = ast.literal_eval(name)
            if isinstance(parsed, list) and len(parsed) == 1:
                name = parsed[0]
            elif isinstance(parsed, list) and len(parsed) == 0:
                return None
            else:
                return ", ".join(parsed)
        except (ValueError, SyntaxError):
            pass # Fall through if it looks like a list but isn't valid python syntax

        return name

    # Case: "Foo Bar (https:/...)" -> "Foo Bar"
    if "(" in name and name.endswith(")"):
        # Remove the parenthesis content at the end
        clean_name = re.sub(r'\s*\([^)]*\)$', '', name).strip()
        return clean_name

    return name
