from keyboard import KeyGrid 

# class wrapping the output of each metric/tracker
#   [self.name] is the name of the metric tracked
#   [self.description] is a description of how to interpret the metric
#   [self.data] is a dict of key, value pairs output by the metric 
class Report():
    # initializes the report
    #   [data_dict] is the dict of data which becomes self.data in the report
    def __init__(self, name, description, data_dict):
        self.name = name
        self.description = description
        self.data = data_dict

    # returns a fancy string containing a full report of the metric
    def __str__(self):
        s = f"| {self.name} \n|    {self.description}"
        for key, val, in self.data.items():
            s = s + f"\n|     {key}:\t {val}"

        return s

# abstract class representing a keyboard property that can be measured/tracked
#   [self.layout] is the Layout which is tracked
#   [self.key_ease_grid] is the KeyGrid which represents how easy each key
#       is to reach/press
class Metric():
    def __init__(self):
       self.layout = None
       self.key_ease_grid = None

    # initialize the layout after object initialization
    def init(self, layout):
        self.layout = layout
        self.key_ease_grid = KeyGrid(layout.grid_spec)
        self.key_ease_grid.fill_with(Metric.key_ease_placement)

    # maps each column to the finger which presses its keys
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

    # maps each finger to its strength/ability to type; higher better
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

    # defines the row id of the home row
    home_row = 1
    
    # string, similar to a key_placement string which defines how 
    # easy each key in the KeyGrid is to press; lower better
    key_ease_placement = (
        "52223  32225"
        "11112  211113"
        "22224  42223"
    )

    # returns true if [key1] and [key2] require the same finger
    def same_finger(self, key1, key2):
        return self.finger(key1) == self.finger(key2)

    # return integer distance between a [key] and the home_row
    def home_row_distance(self, key):
        row, col = self.layout.grid[key]
        return abs(row - home_row)

    # returns the ease of pressing [key]
    def key_ease(self, key):
        row, col = self.layout.grid[key]
        return self.key_ease_grid[row, col]

    # returns the finger which presses [key]
    def finger(self, key):
        row, col = self.layout.grid[key]
        return Metric.col_finger_map[col]

    # returns the hand which presses [key]
    def hand(self, key):
        return self.finger(key)[0]

    # returns a report finalizing the metric
    def report(self):
        pass

    # main component of the public interface for a Metric; will be called when
    # an assessment is run, and will be called on each key in a text stream.
    # allows the Metric to evaluate a condition and respond to the true/false
    # cases.
    #
    # if no condition is necessary, the condition() method defaults to True
    # and the when_false() method defaults to no action.
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
        return True

    def when_true(self, key):
        pass

    def when_false(self, key):
        return 

    def when_space(self, key):
        return 

# a subcategory of Metric which utilize a queue in tracking.
#   [self.queue] is the queue 
#   [self.max_window] is the max size of the queue
class QueueTracker(Metric):
    def __init__(self, max_window=0):
        super().__init__() 
        self.queue = []
        self.max_window = max_window 

    # add a key to the queue, and remove a key if necessary to maintain the
    # max window constraint
    def enqueue(self, key):
        self.queue.append(key)
        if self.max_window > 0:
            if len(self.queue) > self.max_window:
                self.queue.pop(0)
    
    # clear the queue
    def clear(self):
        self.queue = []

   


################################################################################
################################################################################
################################################################################
# Trackers

# tracks the balance of left/right hand keypresses
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

# tracks the percentage of keypresses on the home row, top row, and bottom row
class HomeRowTracker(Metric):
    def __init__(self):
        self.top = 0
        self.home = 0
        self.bottom = 0

    def when_true(self, key):
        row, col = self.layout.grid[key]
        if row == 0:
            self.top = self.top + 1
        elif row == 1:
            self.home = self.home + 1
        elif row == 2:
            self.bottom = self.bottom + 1

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

# tracks the cumulative key ease, aggregated over all keypresses
class KeyEaseTracker(Metric):
    def __init__(self):
        self.cumulative_ease = 0

    def when_true(self, key):
        row, col = self.layout.grid[key]
        key_ease = self.key_ease_grid[row, col]
        self.cumulative_ease = self.cumulative_ease + int(key_ease)

    def report(self):
        report = Report(
            name="Cumulative Key Ease",
            description="Aggregates the total 'ease' score for all keys in the text",
            data_dict={
                "score": self.cumulative_ease
            }
        )

        return report

# tracks the number instances where two consecutive keys are different, but
# require the same finger to press
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

# tracks the number of alternations/hand switches
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

# TODO: implement
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




