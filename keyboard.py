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

# represents the keyboard grid and implements associated indexing methods
class KeyGrid():
    # class of functions passed into the KeyGrid.apply method. Are represented 
    # as objects so that they can retain internal state, and can be defined on 
    # keys, key positions, row changes, or hand changes.
    class KeyGridFunction():
        # defines how the function operates when given an item of the KeyGrid 
        # and its row, col coordinates. Returns the new value of the item at this
        # position
        def __call__(self, item, row, col):
            return item

        # defines how the function operates when it encounters a gap, for split
        # keyboards, between the left and right halves
        def gap(self):
            return

        # defines how the function operates when it encounters a new row
        def row(self):
            return

    def __init__(self, grid_spec):
        self.n_rows = len(grid_spec)
        self.split = isinstance(grid_spec[0], tuple)
        self.rows = []
        self.key_map = {}

        if self.split:
            self._unpack_split(grid_spec)
        else:
            self._unpack(grid_spec)

    # converts a grid specification into a KeyGrid representaton for unsplit 
    # layouts
    def _unpack(self, grid_spec):
        pass

    # converts a grid specification into a KeyGrid representation for split 
    # layouts
    #
    # example_specification = [
    #     (5, 5),
    #     (5, 6),
    #     (5, 5),
    # ]
    # 
    # a specification is a list of order rows (top row first) where each entry
    # is a pair of numbers defining the number typable keys (columns) in each 
    # row; the left and right numbers of the pair denote the left and right
    # hands, respectively.
    def _unpack_split(self, grid_spec):
        for row_spec in grid_spec:
            left, right = row_spec
            row = [[0]*left, [1]*right]
            self.rows.append(row)

    # allows a KeyGrid to be indexed in two ways
    #   1.  supplying a key: returns the tuple coordinates of the key if it 
    #       exists, or None otherwise
    #
    #   2.  supplying a pair: returns the key at the supplied coordinates if 
    #       they exist, or None otherwise
    def __getitem__(self, key):
        if isinstance(key, tuple):
            row_id, col_id = key

            if row_id >= len(self.rows):
                return None

            row = self.rows[row_id] 
            
            if self.split:
                if col_id < len(row[0]):
                    return row[0][col_id]
                elif col_id - len(row[0]) >= len(row[1]):
                    return None
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
            
    # helper function to apply a KeyGridFunction to all keys in a row of keys
    #   [list] the list of keys representing a continuous row of keys
    #   [f] the KeyGridFunction to apply to each key
    #   [row_id] the zero index id (position) of the row
    #   [col_start] what id the column of the first key in the row starts at, 
    #       useful for split layouts
    def _apply_helper(self, list, f, row_id, col_start):
        for i in range(len(list)):
            list[i] = f(list[i], row_id, col_start + i) 

    # applies a KeyGridFunction to all keys in the KeyGrid, and triggers the 
    # appropriate actions when a gap between left/right halves, and when a row
    # change are encountered 
    #   [f] the KeyGridFuncton to apply to each key
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

    # fill all positions of the KeyGrid with ascii values taken from the key
    # placement
    #   [key_placement] a string representing the ordering of keys as they should
    #       be placed onto the grid. filling is done by each row from the top of
    #       the grid, proceeding left to right. space characters (' ') are
    #       ignored
    #
    # example key_placement:
    # qwerty = (
    #     "qwert yuiop"
    #     "asdfg hjkl;'"
    #     "zxcvb nm,./"
    # )
    #
    def fill_with(self, key_placement):
        # class to place keys from a key_placement string onto an empty KeyGrid
        #   [self.key_placment] is the string of keys
        #   [self.pos] is the current position in the string which needs be
        #       placed
        class KeyPlacer(KeyGrid.KeyGridFunction):
            def __init__(self, key_placement):
                self.key_placement = key_placement
                self.pos = 0

            # skipping spaces, returns the next value in self.key_placement
            # as the value new value of an [item] in the KeyGrid
            def __call__(self, item, row, col):
                while self.pos < len(self.key_placement) and self.key_placement[self.pos] == ' ':
                    self.pos = self.pos + 1
                key = self.key_placement[self.pos]
                self.pos = self.pos + 1
                return key

        kp = KeyPlacer(key_placement)
        self.apply(kp)
        self._map_keys()

    # constructs a map index by each key with the value being the key's
    # coordinates in the KeyGrid
    def _map_keys(self):
        class KeyMapper(KeyGrid.KeyGridFunction):
            def __init__(self):
                self.key_map = {}
            
            def __call__(self, item, row, col):
                self.key_map[item] = (row, col)
                return item

        km = KeyMapper()
        self.apply(km)
        self.key_map = km.key_map

    # returns a string representation of the KeyGrid
    def __str__(self):
        class StrMaker(KeyGrid.KeyGridFunction):
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

    # returns a list of all key positions in the KeyGrid, ordered in the
    # following way: starting from the top row, proceeding left to right, moving
    # row by row.
    def ordered_positions(self):
        class PositionRecorder(KeyGrid.KeyGridFunction):
            def __init__(self):
                self.key_positions = []

            def __call__(self, item, row, col):
                self.key_positions.append((row, col)) 
                return item

        pr = PositionRecorder()
        self.apply(pr)
        return pr.key_positions

    # a map which takes an uppercased/shifted key to its lowercased/unshifted
    # correspond
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
    
# A wrapper class for the KeyGrid
class Layout():
    def __init__(self, grid_spec, key_placement):
        self.grid_spec = grid_spec
        self.grid = KeyGrid(grid_spec)
        self.grid.fill_with(key_placement)

    def __str__(self):
        return str(self.grid)
