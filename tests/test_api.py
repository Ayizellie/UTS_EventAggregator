from datetime import datetime, timezone

def test_invalid_event_payload(client):
    """Pastikan sistem menolak event tanpa field wajib"""
    invalid_event = {
        "topic": "invalid.topic",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "test_suite",
        "payload": {"value": 111}
    }
    res = client.post("/publish", json={"events": [invalid_event]})
    assert res.status_code == 400
    data = res.json()
    assert "error" in data or "message" in data


def test_batch_publish(client):
    """Uji publish beberapa event sekaligus"""
    events = [
        {
            "topic": "batch.topic",
            "event_id": f"evt_batch_{i}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "batch_test",
            "payload": {"i": i}
        }
        for i in range(5)
    ]
    res = client.post("/publish", json={"events": events})
    assert res.status_code == 200
    data = res.json()
    assert data["added_to_queue"] == 5

    
    get_res = client.get("/events?topic=batch.topic")
    assert get_res.status_code == 200
    events_data = get_res.json()
    assert events_data["count"] >= 5


def test_multiple_topics_handling(client):
    """Uji sistem mampu menangani beberapa topic"""
    topics = ["topic.a", "topic.b", "topic.c"]
    for t in topics:
        event = {
            "topic": t,
            "event_id": f"evt_{t.replace('.', '_')}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": "multi_topic_test",
            "payload": {"msg": t}
        }
        res = client.post("/publish", json={"events": [event]})
        assert res.status_code == 200

    stats = client.get("/stats").json()
    assert stats["total_topics"] >= 3


def test_event_ordering_by_timestamp(client):
    """Pastikan event terurut berdasarkan timestamp"""
    topic = "order.topic"
    event1 = {
        "topic": topic,
        "event_id": "evt_old",
        "timestamp": "2024-01-01T00:00:00Z",
        "source": "order_test",
        "payload": {"seq": 1}
    }
    event2 = {
        "topic": topic,
        "event_id": "evt_new",
        "timestamp": "2025-01-01T00:00:00Z",
        "source": "order_test",
        "payload": {"seq": 2}
    }

    client.post("/publish", json={"events": [event1, event2]})
    res = client.get(f"/events?topic={topic}")
    data = res.json()

    
    events = data["events"]
    timestamps = [e["timestamp"] for e in events]
    assert timestamps == sorted(timestamps)
