import json
from lum_pe.engine.core import run

def test_run_produces_bundle_and_hash():
    with open("examples/container_nat_general.json","r",encoding="utf-8") as f:
        cont = json.load(f)
    with open("examples/payload_nat_general.json","r",encoding="utf-8") as f:
        payload = json.load(f)
    bundle = run("Evaluar cierre", cont["INPUT"], cont["CONFIG"], cont["MODEL"], payload)
    assert "AUDIT" in bundle and "footprint_sha256" in bundle["AUDIT"]
    assert len(bundle["AUDIT"]["footprint_sha256"]) == 64
    assert bundle["OUTPUT"]["state"] in ("GREEN","AMBER","RED","BLACK")
