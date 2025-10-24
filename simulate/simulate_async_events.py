import asyncio
import aiohttp
import random
import string
import time
from datetime import datetime, timezone

# --------------------------
# CONFIG
# --------------------------
BASE_URL = "http://127.0.0.1:8000"
TOTAL_EVENTS = 5000
DUPLICATE_RATIO = 0.2  # 20% duplikasi
TOPIC = "simula.topic"
BATCH_SIZE = 100  # jumlah event per request

# --------------------------
# UTILITY FUNCTIONS
# --------------------------
def random_event_id():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

def create_event(event_id):
    return {
        "topic": TOPIC,
        "event_id": event_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "async_simulator",
        "payload": {"data": random.randint(1, 1000)}
    }

# --------------------------
# GENERATE EVENTS
# --------------------------
unique_count = int(TOTAL_EVENTS * (1 - DUPLICATE_RATIO))
duplicate_count = TOTAL_EVENTS - unique_count

unique_event_ids = [f"evt{str(i).zfill(4)}" for i in range(unique_count)]
duplicate_event_ids = random.choices(unique_event_ids, k=duplicate_count)
all_event_ids = unique_event_ids + duplicate_event_ids
random.shuffle(all_event_ids)

# --------------------------
# ASYNC SEND
# --------------------------
async def send_batch(session, batch_ids):
    batch_events = [create_event(eid) for eid in batch_ids]
    payload = {"events": batch_events}
    async with session.post(f"{BASE_URL}/publish", json=payload) as resp:
        if resp.status != 200:
            text = await resp.text()
            print("Error sending batch:", text)

# --------------------------
# CLEAR DATABASE
# --------------------------
async def clear_database():
    print("🧹 Clearing database before test...")
    async with aiohttp.ClientSession() as session:
        await session.post(f"{BASE_URL}/clear")  
    print("✅ Database cleared\n")

# --------------------------
# WAIT FOR CONSUMER
# --------------------------
async def wait_for_processing():
    print("⏳ Waiting for consumer to process all events...\n")
    async with aiohttp.ClientSession() as session:
        for sec in range(2, 12, 2):
            await asyncio.sleep(2)
            async with session.get(f"{BASE_URL}/stats") as resp:
                data = await resp.json()
                processed = data.get("received", 0)
                unique = data.get("unique_processed", 0)
                duplicates = data.get("duplicate_dropped", 0)
                print(f"[{sec}s] Processed: {processed}/{TOTAL_EVENTS} events "
                      f"(Unique: {unique}, Duplicates: {duplicates})")
            if processed >= TOTAL_EVENTS:
                break
    print("✅ All events processed in 10 seconds!")

# --------------------------
# MAIN
# --------------------------
async def main():
    await clear_database()

    print("=" * 60)
    print(f"STRESS TEST: {TOTAL_EVENTS} events dengan {DUPLICATE_RATIO*100:.1f}% duplikasi")
    print("=" * 60)

    async with aiohttp.ClientSession() as session:
        tasks = []
        sent_count = 0
        for i in range(0, len(all_event_ids), BATCH_SIZE):
            batch_ids = all_event_ids[i:i+BATCH_SIZE]
            tasks.append(send_batch(session, batch_ids))
            sent_count += len(batch_ids)
            if sent_count % 1000 == 0:
                print(f"Progress: {sent_count}/{TOTAL_EVENTS} events published")
        await asyncio.gather(*tasks)

    print(f"Progress: {TOTAL_EVENTS}/{TOTAL_EVENTS} events published\n")
    await wait_for_processing()

# --------------------------
# RUN
# --------------------------
if __name__ == "__main__":
    start = time.time()
    asyncio.run(main())
    print(f"\n⏱️ Total waktu: {time.time() - start:.2f} detik")
