import requests

res = requests.post(
    'http://127.0.0.1:8080/generate-question',
    json={
        "prompt": "Vrni mi seznam 2 vprašanj kot JSON. Vsak naj ima ključe 'vprasanje', 'odgovor', 'razlaga'. Primer: [{\"vprasanje\": \"Kaj je metafora?\", \"odgovor\": \"Stilska figura\", \"razlaga\": \"Gre za preneseni pomen besed.\"}]"
    }
)
print(res.json())
print("STATUS:", res.status_code)
print("ODGOVOR:", res.text)