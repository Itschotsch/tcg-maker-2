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
    parser = argparse.ArgumentParser(description="Lookup card IDs from names using Notion CSV export.")
    parser.add_argument(
        "input_file", 
        nargs="?", 
        help="Path to a text file containing the list of cards. If omitted or '-', reads from stdin."
    )
    parser.add_argument(
        "--csv", 
        default=DEFAULT_CSV_PATH,
        help="Path to the Notion database CSV file to use for lookup."
    )
    args = parser.parse_args()

    # Load the card database
    name_to_ids = load_card_database(args.csv)

    # Read input lines
    input_lines = []
    if not args.input_file or args.input_file == "-":
        if sys.stdin.isatty():
            print("Enter/paste your card list (press Ctrl+D when finished):", file=sys.stderr)
        input_lines = sys.stdin.readlines()
    else:
        if not os.path.exists(args.input_file):
            print(f"Error: Input file '{args.input_file}' not found.", file=sys.stderr)
            sys.exit(1)
        with open(args.input_file, 'r', encoding='utf-8') as f:
            input_lines = f.readlines()

    # Process each line
    found_ids = set()
    missing_cards = []

    for line in input_lines:
        card_name = parse_input_line(line)
        if not card_name:
            continue
        
        norm_name = normalize_name(card_name)
        if norm_name in name_to_ids:
            for card_id in name_to_ids[norm_name]:
                try:
                    # Attempt to store as integer for proper numeric sorting later
                    found_ids.add(int(card_id))
                except ValueError:
                    found_ids.add(card_id)
        else:
            missing_cards.append(card_name)

    # Output found IDs, sorted
    # We sort integers first, then strings if any
    int_ids = sorted([x for x in found_ids if isinstance(x, int)])
    str_ids = sorted([str(x) for x in found_ids if not isinstance(x, int)])
    
    # Print the unique, sorted IDs to stdout
    for card_id in int_ids:
        print(card_id)
    for card_id in str_ids:
        print(card_id)

    # Print warnings for missing cards to stderr
    if missing_cards:
        print(f"\nWarning: The following {len(missing_cards)} cards could not be found in the database:", file=sys.stderr)
        for card in missing_cards:
            print(f"  - {card}", file=sys.stderr)

if __name__ == "__main__":
    main()
