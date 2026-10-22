import json, subprocess

imgs = json.load(open("policy/images.lock.json"))
missing = []
for name, ref in imgs.items():
    r = subprocess.run(["docker", "image", "inspect", ref], capture_output=True)
    ok = r.returncode == 0
    print(("OK  " if ok else "MISS") + "  " + name + "  " + ref)
    if not ok:
        missing.append((name, ref))
print("---")
print("missing:", len(missing))
