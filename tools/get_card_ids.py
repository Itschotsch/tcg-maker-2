#!/usr/bin/env python3
import sys
import os
import csv
import re

DEFAULT_CSV_PATH = "/mnt/Hauptreservoir/Daten/Benutzer/jan/Projekte/Aetherlab/Anor/tcg-maker-2/process/2026-06-22_00-18-10/csv/data_raw_notion_db_70ddd0aaafb74f56b205e643b0901290.csv"

def normalize_name(name):
    """Normalize card name for robust matching:
    - Strips quotes (standard and smart quotes)
    - Replaces multiple spaces with a single space
    - Converts to lowercase
    """
    if not name:
        return ""
    # Strip smart quotes and standard quotes
    cleaned = re.sub(r'["“”‘’„«»\']', '', name)
    # Collapse multiple whitespaces
    cleaned = " ".join(cleaned.split())
    return cleaned.lower()

def parse_input_line(line):
    """Parses a line like '2 Vertreter der Botengilde' or 'Vertreter der Botengilde'.
    Returns the card name.
    """
    line = line.strip()
    if not line:
        return None
    
    # Match optional quantity (numbers) at the start followed by whitespace
    match = re.match(r'^(\d+)\s+(.+)$', line)
    if match:
        return match.group(2).strip()
    return line

def load_card_database(csv_path):
    """Loads card name to ID mappings from the Notion CSV database."""
    name_to_ids = {}
    if not os.path.exists(csv_path):
        print(f"Error: CSV database file not found at: {csv_path}", file=sys.stderr)
        sys.exit(1)
        
    with open(csv_path, mode='r', encoding='utf-8', errors='replace') as f:
        reader = csv.DictReader(f)
        for row in reader:
            name = row.get("Name")
            card_id = row.get("ID")
            if name and card_id:
                name_clean = normalize_name(name)
                # Keep track of list of IDs because there might be multiple (though usually unique)
                if name_clean not in name_to_ids:
                    name_to_ids[name_clean] = []
                # Make sure the ID is not empty and is clean
                card_id_str = card_id.strip()
                if card_id_str:
                    name_to_ids[name_clean].append(card_id_str)
                    
    return name_to_ids

def main():
    # Setup argument parsing
    import argparse
    parser = argparse.ArgumentParser(description="Lookup card IDs from names using Notion CSV export or JSON card list.")
    
    # Mutually exclusive input formats
    input_group = parser.add_mutually_exclusive_group()
    input_group.add_argument(
        "--tcg-arena-decklist", "-d",
        action="store_true",
        help="Input is a TCG Arena decklist (default)"
    )
    input_group.add_argument(
        "--tcg-arena-card-list", "-c",
        action="store_true",
        help="Input is a TCG Arena card list in JSON format"
    )
    
    # Mutually exclusive output formats
    output_group = parser.add_mutually_exclusive_group()
    output_group.add_argument(
        "--new-line-list",
        action="store_true",
        help="Output IDs as a newline-separated list (default)"
    )
    output_group.add_argument(
        "--comma-separated-list",
        action="store_true",
        help="Output IDs as a comma-separated list"
    )
    
    parser.add_argument(
        "input_file", 
        nargs="?", 
        help="Path to the input file. If omitted or '-', reads from stdin."
    )
    parser.add_argument(
        "--csv", 
        default=DEFAULT_CSV_PATH,
        help="Path to the Notion database CSV file to use for lookup (only used in decklist mode)."
    )
    args = parser.parse_args()

    # Determine input mode (default to decklist)
    is_json_mode = args.tcg_arena_card_list
    
    # Read input text
    if not args.input_file or args.input_file == "-":
        if sys.stdin.isatty():
            mode_name = "JSON card list" if is_json_mode else "card list"
            print(f"Enter/paste your {mode_name} (press Ctrl+D when finished):", file=sys.stderr)
        input_text = sys.stdin.read()
    else:
        if not os.path.exists(args.input_file):
            print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
            sys.exit(1)
        with open(args.input_file, 'r', encoding='utf-8') as f:
            input_text = f.read()

    found_ids = set()
    missing_cards = []

    if is_json_mode:
        import json
        if not input_text.strip():
            print("Error: Input is empty.", file=sys.stderr)
            sys.exit(1)
        try:
            data = json.loads(input_text)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)
            
        if isinstance(data, dict):
            for key, val in data.items():
                card_id = key
                if isinstance(val, dict) and "id" in val:
                    card_id = val["id"]
                card_id_str = str(card_id).strip()
                if card_id_str:
                    try:
                        found_ids.add(int(card_id_str))
                    except ValueError:
                        found_ids.add(card_id_str)
        elif isinstance(data, list):
            for val in data:
                if isinstance(val, dict) and "id" in val:
                    card_id_str = str(val["id"]).strip()
                    if card_id_str:
                        try:
                            found_ids.add(int(card_id_str))
                        except ValueError:
                            found_ids.add(card_id_str)
        else:
            print("Error: JSON must be a dictionary or a list of card objects.", file=sys.stderr)
            sys.exit(1)
    else:
        # Load the card database
        name_to_ids = load_card_database(args.csv)
        
        # Process line by line
        input_lines = input_text.splitlines()
        for line in input_lines:
            card_name = parse_input_line(line)
            if not card_name:
                continue
            
            norm_name = normalize_name(card_name)
            if norm_name in name_to_ids:
                for card_id in name_to_ids[norm_name]:
                    try:
                        found_ids.add(int(card_id))
                    except ValueError:
                        found_ids.add(card_id)
            else:
                missing_cards.append(card_name)

    # Sort the unique IDs
    int_ids = sorted([x for x in found_ids if isinstance(x, int)])
    str_ids = sorted([str(x) for x in found_ids if not isinstance(x, int)])
    
    all_ids = [str(x) for x in int_ids] + str_ids

    # Format output
    if args.comma_separated_list:
        print(",".join(all_ids))
    else:
        for card_id in all_ids:
            print(card_id)

    # Print warnings for missing cards to stderr (only applicable in decklist mode)
    if not is_json_mode and missing_cards:
        print(f"\nWarning: The following {len(missing_cards)} cards could not be found in the database:", file=sys.stderr)
        for card in missing_cards:
            print(f"  - {card}", file=sys.stderr)

if __name__ == "__main__":
    main()
