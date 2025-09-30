class RuleBasedController:
    def __init__(self, fixed_green: int = 20):
        self.fixed_green = fixed_green

    def decide(self, lane_counts):
        # Always cycles equally
        plan = {}
        for lane in lane_counts.keys():
            plan[lane] = self.fixed_green
        return plan
