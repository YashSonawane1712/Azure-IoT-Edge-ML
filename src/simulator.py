import random

class SensorSimulator:
    """Produces realistic-ish simulated environmental sensor readings."""
    def __init__(self, seed=None):
        self.rng = random.Random(seed)
        self.step = 0

    def read(self):
        self.step += 1
        # A few elevated-pollution episodes are intentionally injected.
        episode = (self.step % 18) in range(10, 15)
        pm25 = self.rng.uniform(8, 45) + (self.rng.uniform(35, 100) if episode else 0)
        pm10 = pm25 * self.rng.uniform(1.2, 2.0)
        co2 = self.rng.uniform(420, 900) + (self.rng.uniform(300, 700) if episode else 0)
        voc = self.rng.uniform(40, 180) + (self.rng.uniform(100, 350) if episode else 0)
        return {
            "temperature": round(self.rng.uniform(18, 38), 2),
            "humidity": round(self.rng.uniform(25, 85), 2),
            "pm25": round(pm25, 2),
            "pm10": round(pm10, 2),
            "co2": round(co2, 2),
            "voc": round(voc, 2),
        }
