import keyboard

# TODO: under construction
prediction_default_settings = {
    "rolls": "inward",
    "finger_strength": [1, 3, 5, 5, 5, 5, 3, 1],
    "row_strength": [1, 3, 2],
    "col_strength": [1, 3, 5, 4, 4, 5, 3, 1, 1],
}

class TwoKeyPredict():
    def __init__(self, grid_spec):
        self.grid_spec = grid_spec
        self.key_ease_grid = keyboard.KeyGrid(grid_spec)

        self._generate_key_ease_fill()

    def _generate_key_ease_fill(self):

        

    def generate_predict_map(self, prev_key, key):
        