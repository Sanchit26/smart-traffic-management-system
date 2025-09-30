class RLAgent:
    def __init__(self, base_time=10, max_time=60):
        self.base_time = base_time
        self.max_time = max_time

    def decide(self, lane_counts):
        total = sum(lane_counts.values()) or 1
        plan = {}
        for lane, count in lane_counts.items():
            share = count / total
            green_time = int(self.base_time + share * (self.max_time - self.base_time))
            plan[lane] = green_time
        return plan
