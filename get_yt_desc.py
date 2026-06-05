import json, sys
d = json.load(sys.stdin)
desc = d.get('description', 'N/A')
outpath = sys.argv[1]
with open(outpath, 'w', encoding='utf-8') as f:
    f.write(desc[:5000])
