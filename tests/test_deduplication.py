import pytest
from src.dedup_store import DedupStore

@pytest.fixture
def temp_db(tmp_path):
    """Fixture DedupStore sementara"""
    db_path = tmp_path / "dedup_test.db"
    store = DedupStore(db_path=str(db_path))
    return store


def test_add_and_detect_duplicate(temp_db):
    """Pastikan event duplikat tidak diproses dua kali"""
    topic = "demo.topic"
    event_id = "evt_dupe_001"

    # pertama kali belum ada
    assert not temp_db.is_duplicate(topic, event_id)

    # tambahkan event
    added = temp_db.add_event(topic, event_id)
    assert added is True
    assert temp_db.is_duplicate(topic, event_id)

    # tambahkan lagi (duplikat)
    added_again = temp_db.add_event(topic, event_id)
    assert added_again is False  # harusnya ditolak


def test_multiple_topics_and_events(temp_db):
    """Pastikan beberapa topik dan event tersimpan benar"""
    temp_db.add_event("topic.a", "evt1")
    temp_db.add_event("topic.a", "evt2")
    temp_db.add_event("topic.b", "evt3")

    all_events = temp_db.get_all_events()
    assert len(all_events) == 3

    topics = temp_db.get_topics()
    assert set(topics) == {"topic.a", "topic.b"}
