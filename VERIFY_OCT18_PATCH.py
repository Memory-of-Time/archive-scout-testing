"""Check that every v1.2.4 October 18 recovery patch file was installed."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parent
checks=json.loads((root/'OCT18_PATCH_MANIFEST.json').read_text())['patch_files']
failed=False
for name, expected in checks.items():
    path=root/name
    actual=hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else 'MISSING'
    ok=(actual==expected)
    print(f'{"OK" if ok else "MISMATCH"}: {name}')
    failed|=not ok
sys.exit(1 if failed else 0)
