import logging
from fastapi import FastAPI
from src.models import EventBatch
from src.dedup_store import DedupStore
from src.event_queue import EventQueue
from datetime import datetime
from fastapi.responses import JSONResponse

# setup logging biar muncul di terminal
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)

app = FastAPI()
dedup = DedupStore()
queue = EventQueue()

# waktu mulai server
start_time = datetime.utcnow()

# statistik global
stats_data = {
    "received": 0,
    "unique_processed": 0,
    "duplicate_dropped": 0
}


# ---------------------------
# Publish endpoint
# ---------------------------
@app.post("/publish")
def publish(batch: dict):  # ubah sementara jadi dict biar manual validation bisa jalan
    if "events" not in batch or not isinstance(batch["events"], list):
        return JSONResponse(status_code=400, content={"error": "Missing 'events' list"})

    for event in batch["events"]:
        required_fields = ["topic", "event_id", "timestamp", "source", "payload"]
        for f in required_fields:
            if f not in event:
                return JSONResponse(status_code=400, content={"error": f"Missing required field: {f}"})
    
    # baru konversi ke model EventBatch kalau lolos validasi
    batch_model = EventBatch(**batch)

    # lanjut proses seperti sebelumnya
    added_count = 0
    for event in batch_model.events:
        stats_data["received"] += 1
        if dedup.add_event(event.topic, event.event_id):
            queue.add_event({
                "topic": event.topic,
                "event_id": event.event_id,
                "timestamp": event.timestamp,
                "source": event.source,
                "payload": event.payload
            })
            added_count += 1
            stats_data["unique_processed"] += 1
            logging.info(f"✅ New event added: ({event.topic}, {event.event_id})")
        else:
            stats_data["duplicate_dropped"] += 1
            logging.warning(f"⚠️ Duplicate detected, dropped: ({event.topic}, {event.event_id})")

    logging.info(
        f"📦 Batch received: {len(batch_model.events)} | Added: {added_count} | Duplicates: {len(batch_model.events) - added_count}"
    )
    return {"status": "ok", "received": len(batch_model.events), "added_to_queue": added_count}

# ---------------------------
# Ambil semua event
# ---------------------------
@app.get("/events")
def get_events(topic: str = None):
    """Mengambil semua event dari queue, difilter berdasarkan topic."""
    events = [e for e in queue.queue if topic is None or e["topic"] == topic]
    events_sorted = sorted(events, key=lambda x: x["timestamp"])
    return {"events": events_sorted, "count": len(events_sorted)}


# ---------------------------
# Statistik lengkap
# ---------------------------
@app.get("/stats")
def stats():
    """Menampilkan statistik jumlah topik, total event, dan status sistem."""
    topics = dedup.get_topics()
    total_events = len(dedup.get_all_events())
    topic_counts = {t: len(dedup.get_all_events(t)) for t in topics}
    uptime_seconds = (datetime.utcnow() - start_time).total_seconds()

    return {
        "received": stats_data["received"],
        "unique_processed": stats_data["unique_processed"],
        "duplicate_dropped": stats_data["duplicate_dropped"],
        "total_topics": len(topics),
        "total_events": total_events,
        "events_per_topic": topic_counts,
        "queue_length": len(queue.queue),
        "uptime": f"{uptime_seconds:.2f}s"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)