import json
from pathlib import Path


class GlossaryService:
    def __init__(self):
        path = Path(__file__).parent / 'data' / 'glossary.zh-CN.json'
        raw = json.loads(path.read_text(encoding='utf-8'))
        self.items = []
        for group_name, group_items in raw.items():
            for key, value in group_items.items():
                self.items.append({'key': key.lower(), 'value': value, 'group': group_name})

    def explain(self, source_text, limit=12):
        text = source_text.lower()
        found = []
        for row in sorted(self.items, key=lambda x: len(x['key']), reverse=True):
            if row['key'] in text:
                found.append(row)
            if len(found) >= limit:
                break
        if not found:
            return '没有识别到专有术语。'
        return '\n'.join(row['key'] + ' = ' + row['value'] for row in found)
