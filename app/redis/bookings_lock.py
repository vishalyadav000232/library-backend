from app.redis.client import redis_client
LOCK_EXPIRY = 300




def lock_seat(seat_id, shift_id, date):
    key = f"seat_lock:{seat_id}:{shift_id}:{date}"
    return redis_client.set(key, "locked", nx=True, ex=LOCK_EXPIRY)

def unlock_seat(seat_id, shift_id, date):
    key = f"seat_lock:{seat_id}:{shift_id}:{date}"
    redis_client.delete(key)