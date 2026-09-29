import json
import sys

transcript_path = r"C:\Users\RAMESH PATARE\.gemini\antigravity-ide\brain\f08df99c-9f4a-4a38-abbf-379e8b520ae4\.system_generated\logs\transcript_full.jsonl"
raw_data_path = r"c:\Users\RAMESH PATARE\OneDrive\Desktop\SIH\SIH26103\backend\raw_data_2.txt"

with open(transcript_path, 'r', encoding='utf-8') as f:
    for line in f:
        data = json.loads(line)
        if data.get('type') == 'USER_INPUT':
            content = data.get('content', '')
            with open(raw_data_path, 'w', encoding='utf-8') as out_f:
                out_f.write(content)
            print("Successfully extracted first USER_INPUT to raw_data_2.txt")
            sys.exit(0)

print("Could not find any USER_INPUT")
sys.exit(1)
