import csv
import json
import ssl
import sys
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

_SSL_CTX = ssl.create_default_context()
_SSL_CTX.check_hostname = False
_SSL_CTX.verify_mode = ssl.CERT_NONE

COLLECTION_URL = "https://tamulib-dc-labs.github.io/custom-iiif-manifests/collections/service-maps.json"
OUTPUT_FILE = "originals.csv"
WORKERS = 10


def fetch_json(url):
    with urllib.request.urlopen(url, context=_SSL_CTX) as resp:
        return json.loads(resp.read())


def get_original_filenames(manifest_url):
    manifest = fetch_json(manifest_url)
    for entry in manifest.get("metadata", []):
        labels = entry.get("label", {}).get("en", [])
        if labels and labels[0] == "Original Filenames":
            values = entry.get("value", {}).get("en", [])
            return "|".join(values)
    print(f"WARNING: no 'Original Filenames' in {manifest_url}", file=sys.stderr)
    return ""


def main():
    print(f"Fetching collection: {COLLECTION_URL}")
    collection = fetch_json(COLLECTION_URL)
    items = collection.get("items", [])
    print(f"Found {len(items)} manifests — fetching in parallel…")

    results = {}
    with ThreadPoolExecutor(max_workers=WORKERS) as pool:
        futures = {pool.submit(get_original_filenames, item["id"]): item["id"] for item in items}
        completed = 0
        for future in as_completed(futures):
            manifest_url = futures[future]
            results[manifest_url] = future.result()
            completed += 1
            if completed % 20 == 0 or completed == len(items):
                print(f"  {completed}/{len(items)}")

    with open(OUTPUT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Id", "original"])
        for item in items:
            writer.writerow([item["id"], results[item["id"]]])

    print(f"Wrote {len(items)} rows to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
