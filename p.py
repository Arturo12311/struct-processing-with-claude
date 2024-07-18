import json
with open('_og_structs.json', 'r') as f:
    og = json.load(f)


ns = set()
nl = []
for k, v in og.items():
    for x, y in v.items():
        if y["nullable"] == True and y["type"] == "struct":
            ns.add(y["value"])
            nl.append(y["value"])

print(ns)
print(sorted(nl))
print(len(ns))
print(len(nl))

nns = set()
nnl = []
for k, v in og.items():
    for x, y in v.items():
        if y["value"] in ns and y["nullable"] == False:
            nns.add(y["value"])
            nnl.append(y["value"])

with open('_final_form.json', 'r') as f:
    z = json.load(f)

count = 0
import re
for k, v in z.items():
    for x, y in v.items():
        if isinstance(y, str) and re.match("FTz.*", y):
            if y[3:] in ns:
                y = y + "0"
                v[x] = y
                count+= 1

with open('_final_form_v2.json', 'w') as f:
    json.dump(z, f, indent = 2)