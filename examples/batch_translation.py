"""Batch translation example."""
import csv
import sys
from money_api import MoneyAPI
from pathlib import Path


def translate_csv(
    client: MoneyAPI,
    input_file: str,
    output_file: str,
    source_lang: str,
    target_lang: str
):
    """Translate text from CSV file.

    Args:
        client: Money API client
        input_file: Input CSV file path
        output_file: Output CSV file path
        source_lang: Source language code
        target_lang: Target language code
    """
    print(f"📄 Reading {input_file}...")

    # Read input CSV
    with open(input_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    if not rows:
        print("❌ No data found in input file")
        return

    print(f"📝 Found {len(rows)} rows to translate")
    print(f"🌍 Translating from {source_lang} to {target_lang}...")

    total_cost = 0.0
    translated_rows = []

    for i, row in enumerate(rows, 1):
        text = row.get('text', '')

        if not text:
            translated_rows.append({**row, 'translation': ''})
            continue

        try:
            # Translate
            response = client.text.translate(
                text=text,
                source_lang=source_lang,
                target_lang=target_lang
            )

            translation = response['translated_text']
            cost = response['cost']
            total_cost += cost

            translated_rows.append({
                **row,
                'translation': translation
            })

            print(f"✅ [{i}/{len(rows)}] Translated (${cost:.4f})")

        except Exception as e:
            print(f"❌ [{i}/{len(rows)}] Error: {e}")
            translated_rows.append({**row, 'translation': '[ERROR]'})

    # Write output CSV
    print(f"\n💾 Writing to {output_file}...")

    fieldnames = list(rows[0].keys()) + ['translation']

    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(translated_rows)

    print(f"\n✨ Translation complete!")
    print(f"📊 Total cost: ${total_cost:.2f}")


def main():
    """Run batch translation."""
    if len(sys.argv) < 5:
        print("Usage: python batch_translation.py <api_key> <input.csv> <output.csv> <source_lang> <target_lang>")
        print("Example: python batch_translation.py sk_... input.csv output.csv en es")
        sys.exit(1)

    api_key = sys.argv[1]
    input_file = sys.argv[2]
    output_file = sys.argv[3]
    source_lang = sys.argv[4]
    target_lang = sys.argv[5]

    # Validate input file
    if not Path(input_file).exists():
        print(f"❌ Input file not found: {input_file}")
        sys.exit(1)

    # Initialize client
    client = MoneyAPI(api_key=api_key)

    # Run translation
    translate_csv(client, input_file, output_file, source_lang, target_lang)


if __name__ == "__main__":
    main()
