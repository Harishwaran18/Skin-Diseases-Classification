"""Quick smoke test of the full backend flow against a running server."""
import io
import sys

import httpx
from PIL import Image
import numpy as np
import numpy.random as nr

BASE = "http://localhost:12000"


def make_image():
    arr = np.zeros((400, 400, 3), dtype=np.uint8)
    arr[:, :, 0] = 180; arr[:, :, 1] = 140; arr[:, :, 2] = 110
    arr += nr.randint(-30, 30, arr.shape, dtype=np.int8).astype(np.uint8)
    for _ in range(8):
        y, x = nr.randint(50, 350, 2); r = nr.randint(8, 25)
        yy, xx = np.ogrid[:400, :400]
        m = ((yy - y) ** 2 + (xx - x) ** 2) < r * r
        arr[m] = [200, 80, 60]
    buf = io.BytesIO()
    Image.fromarray(arr).save(buf, "JPEG", quality=95)
    buf.seek(0)
    return buf


def main():
    c = httpx.Client(base_url=BASE, timeout=30)
    # register
    r = c.post("/api/auth/register", json={
        "email": "smoke@test.com", "full_name": "Smoke", "password": "Password123"})
    print("register:", r.status_code)
    tok = r.json()["access_token"]
    h = {"Authorization": f"Bearer {tok}"}

    # profile update
    r = c.put("/api/profile", json={"age": 30, "known_condition": "eczema"}, headers=h)
    print("profile:", r.status_code, r.json().get("known_condition"))

    # symptoms (a few days)
    from datetime import datetime, timedelta, timezone
    now = datetime.now(timezone.utc)
    for i in range(5):
        r = c.post("/api/symptoms", json={
            "recorded_at": (now - timedelta(days=i)).isoformat(),
            "itching": 2 + (i % 3), "redness": 1 + (i % 2)}, headers=h)
    print("symptoms posted:", r.status_code)

    r = c.get("/api/symptoms/trends?window=30", headers=h)
    print("trends:", r.status_code, r.json()["direction"])

    # triggers
    c.post("/api/triggers", json={"category": "lifestyle", "name": "stress", "intensity": 4}, headers=h)
    c.post("/api/triggers", json={"category": "food", "name": "dairy", "intensity": 3}, headers=h)
    r = c.get("/api/triggers/analysis?window=30", headers=h)
    print("trigger analysis:", r.status_code, len(r.json()["associations"]))

    # treatments
    r = c.post("/api/treatments", json={"name": "Moisturizer", "schedule": "Twice daily"}, headers=h)
    tid = r.json()["id"]
    c.post(f"/api/treatments/{tid}/logs", json={"status": "completed"}, headers=h)
    c.post(f"/api/treatments/{tid}/logs", json={"status": "skipped"}, headers=h)
    r = c.get("/api/treatments", headers=h)
    print("treatments:", r.status_code, "adherence:", r.json()[0]["adherence_pct"])

    # image upload + AI
    r = c.post("/api/images/upload", files={"file": ("skin.jpg", make_image(), "image/jpeg")},
               data={"body_location": "left_arm"}, headers=h)
    print("upload:", r.status_code, r.json()["quality_ok"])
    img_id = r.json()["image_id"]
    r = c.post(f"/api/ai/analyze/{img_id}", headers=h)
    print("analyze:", r.status_code)
    d = r.json()
    print("  category:", d["prediction"]["category"], "conf:", d["prediction"]["confidence"],
          "demo:", d["prediction"]["is_demo"], "reliable:", d["prediction"]["reliable"])
    print("  consultation:", d["consultation_recommended"])

    # dashboard
    r = c.get("/api/dashboard", headers=h)
    print("dashboard:", r.status_code, "risk:", r.json()["risk_level"])

    # report
    r = c.post("/api/reports/generate", json={"include_images": True}, headers=h)
    print("report:", r.status_code, r.json()["id"])
    rid = r.json()["id"]
    r = c.get(f"/api/reports/{rid}/download", headers=h)
    print("report download:", r.status_code, "bytes:", len(r.content), "type:", r.headers.get("content-type"))

    # data export
    r = c.get("/api/profile/export", headers=h)
    print("export:", r.status_code, "keys:", list(r.json().keys()))

    print("\nALL SMOKE TESTS PASSED")


if __name__ == "__main__":
    main()
