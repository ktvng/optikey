# Author: Kevin Tang
from layout import KeyGrid

class Report():
    def __init__(self, name, description, data_dict):
        self.name = name
        self.description = description
        self.data = data_dict

    def __str__(self):
        s = f"| {self.name} \n|    {self.description}"
        for key, val, in self.data.items():
            s = s + f"\n|     {key}:\t {val}"

        return s


class Metric():
    def __init__(self):
       self.layout = None
       self.key_ease_grid = None


    def init(self, layout):
        self.layout = layout
        self.key_ease_grid = KeyGrid(layout.grid_spec)
        self.key_ease_grid.fill_with(Metric.key_ease_placement)


    col_finger_map = {
        0: "L_pinky",
        1: "L_ring",
        2: "L_middle",
        3: "L_index",
        4: "L_index",

        5: "R_index",
        6: "R_index",
        7: "R_middle",
        8: "R_ring",
        9: "R_pinky",
        10: "R_pinky"
    }

    # higher better
    finger_strength_map = {
        "L_pinky": 1,
        "L_ring": 2,
        "L_middle": 5,
        "L_index": 4,

        "R_pinky": 1,
        "R_ring": 2,
        "R_middle": 5,
        "R_index": 4
    }

    home_row = 1
    
    # lower better
    key_ease_placement = (
        "52223  32225"
        "11112  211113"
        "22224  42223"
    )

    def same_finger(self, key1, key2):
        return self.finger(key1) == self.finger(key2)

    def home_row_distance(self, key):
        row, col = self.layout.grid[key]
        return abs(row - home_row)

    def key_ease(self, key):
        row, col = self.layout.grid[key]
        return self.key_ease_grid[row, col]

    def finger(self, key):
        row, col = self.layout.grid[key]
        return Metric.col_finger_map[col]

    def hand(self, key):
        return self.finger(key)[0]

    def report(self):
        pass
    
    def evaluate(self, key):
        if key == ' ':
            self.when_space(key)
            return

        if self.layout.grid[key] is None:
            return

        if self.condition(key):
            self.when_true(key)
        else:
            self.when_false(key)

    def condition(self, key):
        pass
    
    def when_true(self, key):
        pass

    def when_false(self, key):
        pass

    def when_space(self, key):
        return 


    
    
class QueueTracker(Metric):
    def __init__(self, max_window=0):
        super().__init__() 
        self.queue = []
        self.max_window = max_window 

    def enqueue(self, key):
        self.queue.append(key)
        if self.max_window > 0:
            if len(self.queue) > self.max_window:
                self.queue.pop(0)

    def clear(self):
        self.queue = []

   

class HandBalanceTracker(Metric):
    def __init__(self):
        self.n_left = 0
        self.n_right = 0

    def condition(self, key):
        return self.hand(key) == 'R'

    def when_true(self, key):
        self.n_right = self.n_right + 1
    
    def when_false(self, key):
        self.n_left = self.n_left + 1
        
    def report(self):
        report = Report(
            name="Hand Balance",
            description="Percentage of keys typed using the left hand",
            data_dict={
                "ratio": self.n_left / (self.n_left + self.n_right)
            }
        )

        return report 

class HomeRowTracker(Metric):
    def __init__(self):
        self.top = 0
        self.home = 0
        self.bottom = 0

    def condition(self, key):
        return True

    def when_true(self, key):
        row, col = self.layout.grid[key]
        if row == 0:
            self.top = self.top + 1
        elif row == 1:
            self.home = self.home + 1
        elif row == 2:
            self.bottom = self.bottom + 1

    def when_false(self, key):
        return

    def report(self):
        report = Report(
            name="Row percentage",
            description="The percentage of keys typable via the each row",
            data_dict={
                "home": self.home / (self.top + self.home + self.bottom),
                "top": self.top / (self.top + self.home + self.bottom),
                "bottom": self.bottom / (self.top + self.home + self.bottom)
            }
        )

        return report

class KeyEaseTracker(Metric):
    def __init__(self):
        self.cumulative_ease = 0

    def condition(self, key):
        return True

    def when_true(self, key):
        row, col = self.layout.grid[key]
        key_ease = self.key_ease_grid[row, col]
        self.cumulative_ease = self.cumulative_ease + int(key_ease)

    def when_false(self, key):
        return

    def report(self):
        report = Report(
            name="Cumulative Key Ease",
            description="Aggregates the total 'ease' score for all keys in the text",
            data_dict={
                "score": self.cumulative_ease
            }
        )

        return report

class RepeatFingerTracker(QueueTracker):
    def __init__(self):
        super().__init__(max_window=1)
        self.repeats = 0

    def condition(self, key):
        if len(self.queue) > 0:
            prev_key = self.queue[-1]
            if(key == prev_key):
                return False
            return self.same_finger(key, prev_key)
        return False

    def when_true(self, key):
        self.repeats = self.repeats + 1
        self.enqueue(key)

    def when_false(self, key):
        self.enqueue(key)

    def report(self):
        report = Report(
            name="Repeated Fingers",
            description="Counts number of times the same finger is used on two consecutive, different keys",
            data_dict={
                "repeats": self.repeats
            }
        )
        return report 

class AlternationTracker(QueueTracker):
    def __init__(self):
        super().__init__(max_window=1)
        self.hand_switches = 0

    def condition(self, key):
        if len(self.queue) > 0:
            prev_key = self.queue[-1]
            return self.hand(prev_key) != self.hand(key)

        return False

    def when_true(self, key):
        self.hand_switches = self.hand_switches + 1
        self.enqueue(key)
    
    def when_false(self, key):
        self.enqueue(key)

    def report(self):
        report = Report(
            name="Hand alternations",
            description="Counts the number of times each successive key switches hands",
            data_dict={
                "switches": self.hand_switches
            }
        )

        return report
        
# class InsideRollTracker(QueueTracker):
#     def __init__(self):
#         super().__init__(max_window=10)
#         self.inside_rolls = 0

#     def condition(self, key):
#         hand = self.hand(key)
#         row, col = self.layout.grid[key]

#         last_row, last_col = self.layout.grid[self.queue[-1]]

#         if hand == 'L':
#             f




