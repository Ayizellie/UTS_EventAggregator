from src.dedup_store import DedupStore

def test_persistence_across_restart(tmp_path):
    """Pastikan data tetap ada setelah 'restart'"""
    db_path = tmp_path / "persist_test.db"

    
    store1 = DedupStore(db_path=str(db_path))
    store1.add_event("demo.topic", "evt_persist_001")

    
    assert store1.is_duplicate("demo.topic", "evt_persist_001")

    
    store2 = DedupStore(db_path=str(db_path))

    
    assert store2.is_duplicate("demo.topic", "evt_persist_001")


def test_persistence_multiple_events(tmp_path):
    """Pastikan banyak event tersimpan dan terbaca ulang"""
    db_path = tmp_path / "persist_multiple.db"

    
    store1 = DedupStore(db_path=str(db_path))
    events = [("demo.topic", f"evt_{i}") for i in range(5)]
    for t, e in events:
        store1.add_event(t, e)

    
    store2 = DedupStore(db_path=str(db_path))
    all_events = store2.get_all_events("demo.topic")

    assert len(all_events) == 5
    for _, eid in all_events:
        assert eid.startswith("evt_")
