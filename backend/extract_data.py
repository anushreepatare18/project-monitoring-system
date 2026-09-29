import json
import sys

transcript_path = r"C:\Users\RAMESH PATARE\.gemini\antigravity-ide\brain\f08df99c-9f4a-4a38-abbf-379e8b520ae4\.system_generated\logs\transcript_full.jsonl"
raw_data_path = r"c:\Users\RAMESH PATARE\OneDrive\Desktop\SIH\SIH26103\backend\raw_data_2.txt"

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            content = data.get('content', '')
            if '==Start of PDF==' in content:
                # write the content to raw_data_2.txt
                with open(raw_data_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(content)
                print("Successfully extracted PDF data to raw_data_2.txt")
                sys.exit(0)

print("Could not find the user input with PDF data")
sys.exit(1)
