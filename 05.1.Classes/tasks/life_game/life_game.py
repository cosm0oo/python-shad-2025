class LifeGame(object):
    """
    Class for Game life
    """

    EMPTY = 0
    ROCK = 1
    FISH = 2
    SHRIMP = 3

    def __init__(self, ocean):
        self._ocean = [list(row) for row in ocean]
        self._rows = len(self._ocean)
        self._cols = len(self._ocean[0]) if self._rows > 0 else 0

    def get_next_generation(self):
        next_ocean = [[self._next_cell_value(i, j) for j in range(self._cols)] for i in range(self._rows)]
        self._ocean = next_ocean
        return [list(row) for row in self._ocean]

    def _next_cell_value(self, row_index, col_index):
        current = self._ocean[row_index][col_index]
        if current == self.ROCK:
            return self.ROCK
        if current == self.FISH:
            fish_neighbors = self._count_neighbors_of_type(row_index, col_index, self.FISH)
            if fish_neighbors == 2 or fish_neighbors == 3:
                return self.FISH
            return self.EMPTY
        if current == self.SHRIMP:
            shrimp_neighbors = self._count_neighbors_of_type(row_index, col_index, self.SHRIMP)
            if shrimp_neighbors == 2 or shrimp_neighbors == 3:
                return self.SHRIMP
            return self.EMPTY
        fish_neighbors = self._count_neighbors_of_type(row_index, col_index, self.FISH)
        if fish_neighbors == 3:
            return self.FISH
        shrimp_neighbors = self._count_neighbors_of_type(row_index, col_index, self.SHRIMP)
        if shrimp_neighbors == 3:
            return self.SHRIMP
        return self.EMPTY

    def _count_neighbors_of_type(self, row_index, col_index, cell_type):
        count = 0
        for d_row in (-1, 0, 1):
            for d_col in (-1, 0, 1):
                if d_row == 0 and d_col == 0:
                    continue
                n_row = row_index + d_row
                n_col = col_index + d_col
                if 0 <= n_row < self._rows and 0 <= n_col < self._cols:
                    if self._ocean[n_row][n_col] == cell_type:
                        count += 1
        return count
