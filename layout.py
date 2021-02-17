# Author: Kevin Tang

# Ortholinear split layout
# 5----  5-----
# 5----  6------
# 5----  5-----

osl = [
    (5, 5),
    (5, 6),
    (5, 5),
]

qwerty = (
    "qwert yuiop"
    "asdfg hjkl;'"
    "zxcvb nm,./"
)

colemak = (
    "qwfpg jluy;"
    "arstd hneio'"
    "zxcvb km,./"
)

dvorak = (
    "',.py fgcrl"
    "aoeui dhtns-"
    ";qjkx bmwvz"
)

custom = (
    "abcde fghij"
    "klmno pqrstu"
    "vwxyz ;',./"
)

class KeyPosition():
    def __init__(self, hand, row, col):
        self.hand = hand
        self.row = row
        self.col = col

class KeyGrid():
    def __init__(self, grid_spec):
        self.n_rows = len(grid_spec)
        self.split = isinstance(grid_spec[0], tuple)
        self.rows = []
        self.key_map = {}

        if self.split:
            self.unpack_split(grid_spec)
        else:
            self.unpack(grid_spec)


    def unpack(self, grid_spec):
        pass

    def unpack_split(self, grid_spec):
        for row_spec in grid_spec:
            left, right = row_spec
            row = [[0]*left, [1]*right]
            self.rows.append(row)

    def __getitem__(self, key):
        if isinstance(key, tuple):
            row_id, col_id = key
            row = self.rows[row_id] 
            
            if self.split:
                if col_id < len(row[0]):
                    return row[0][col_id]
                else:
                    return row[1][col_id - len(row[0])]
            else:
                return row[col_id]
        
        else:
            unshifted = KeyGrid.unshift_map.get(key)
            if self.key_map.get(key) is not None:
                return self.key_map.get(key) 
            elif self.key_map.get(unshifted) is not None:
                return self.key_map.get(unshifted)

            return None 
            
            

    def _apply_helper(self, list, f, row_id, col_start):
        for i in range(len(list)):
            list[i] = f(list[i], row_id, col_start + i) 

    def apply(self, f):
        for row_id, row in enumerate(self.rows):
            if self.split:
                left, right = row
                self._apply_helper(left, f, row_id, 0)
                f.gap()
                self._apply_helper(right, f, row_id, len(left))
            else:
                self._apply_helper(row, f, row_id, 0)
            f.row()

    def fill_with(self, key_placement):
        class KeyPlacer():
            def __init__(self, key_placement):
                self.key_placement = key_placement
                self.pos = 0

            def __call__(self, item, row, col):
                while self.pos < len(self.key_placement) and self.key_placement[self.pos] == ' ':
                    self.pos = self.pos + 1
                key = self.key_placement[self.pos]
                self.pos = self.pos + 1
                return key

            def gap(self):
                return None

            def row(self):
                return None

        kp = KeyPlacer(key_placement)
        self.apply(kp)
        self._map_keys()

    def _map_keys(self):
        class KeyMapper():
            def __init__(self):
                self.key_map = {}
            
            def __call__(self, item, row, col):
                self.key_map[item] = (row, col)
                return item

            def gap(self):
                return None
            
            def row(self):
                return None

        km = KeyMapper()
        self.apply(km)
        self.key_map = km.key_map

    def __str__(self):
        class StrMaker():
            def __init__(self):
                self.str = ""

            def __call__(self, item, row, col):
                self.str = self.str + " " + str(item)
                return item

            def gap(self):
                self.str = self.str + "\t"
            
            def row(self):
                self.str = self.str + "\n"

        sm = StrMaker()
        self.apply(sm)
        return sm.str
    
    unshift_map = {
        'A': 'a',
        'B': 'b',
        'C': 'c',
        'D': 'd',
        'E': 'e',
        'F': 'f',
        'G': 'g',
        'H': 'h',
        'I': 'i',
        'J': 'j',
        'K': 'k',
        'L': 'l',
        'M': 'm',
        'N': 'n',
        'O': 'o',
        'P': 'p',
        'Q': 'q',
        'R': 'r',
        'S': 's',
        'T': 't',
        'U': 'u',
        'V': 'v',
        'W': 'w',
        'X': 'x',
        'Y': 'y',
        'Z': 'z',
        ':': ';',
        '<': ',',
        '>': '.',
        '?': '/',
    }
    
    
class Layout():
    def __init__(self, grid_spec, key_placement):
        self.grid_spec = grid_spec
        self.grid = KeyGrid(grid_spec)
        self.grid.fill_with(key_placement)


    def __str__(self):
        return str(self.grid)

