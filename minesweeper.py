import itertools
import random
import copy

class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        # we can assume two things without an algo count == 0 means no mines and count == len(cells) means all mines

        #print('In known mines')
        if self.count == 0:
            return None
        elif len(self.cells) == self.count:
            return self.cells

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        #print('In known safes')
        # using only self.cells and self.count, return a set of all the cells that are known to be safe
        # if the count is 0, then all cells are safe
        # if the count is equal to the length of the cells, then all cells are mines

        if len(self.cells) == self.count:
            return None
        elif self.count == 0:
            return self.cells

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """     
        #print('In mark mine')   
        # Since we are modifying count we will need to check if the cell is in the set first
        if cell in self.cells:
            self.cells.discard(cell)
            self.count -= 1

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        #print('In mark safe')
        # since we only need to get rid of the cell we can use discard to remove it if its not there no worries it wont throw an error
        self.cells.discard(cell)


class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def check_neighbors(self, cell, count):
        """
        takes in a safe cell and returns a set of all the neighbors of that cell
        checks edge cases for index errors or -1 values that would cause python to access end of arr
        used to create a sentence for the knowledge base
        does not add known safes, does add known mines???
        """
        neighbors = set()
        x = cell[0]
        y = cell[1]
        
        # get all neighbors regardless if they are in bounds or not
        topLeft = (x - 1, y - 1)
        top = (x - 1, y)
        topRight = (x - 1, y + 1)
        rightCenter = (x, y + 1)
        bottomRight = (x + 1, y + 1)
        bottom = (x + 1, y)
        bottomLeft = (x + 1, y - 1)
        leftCenter = (x, y - 1)
        
        neighborArr = [topLeft, top, topRight, rightCenter, bottomRight, bottom, bottomLeft, leftCenter]
        
        # loop over the list of neighbors and check if they are in bounds if they are we add them to our set
        for neighbor in neighborArr:
            if neighbor[0] in range(self.height) and neighbor[1] in range(self.width):
                if neighbor not in self.safes and neighbor not in self.mines:
                    neighbors.add(neighbor)
                if neighbor in self.mines:
                    count -= 1
        return {'cells': neighbors, 'count': count}

 
    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """
        print('In add knowledge')
        self.moves_made.add(cell)  # Step 1
        self.mark_safe(cell)  # marks the cell as safe
        neighborResources = self.check_neighbors(cell, count)
        if len(neighborResources['cells']) != 0:
            print(neighborResources)
            self.knowledge.append(Sentence(neighborResources['cells'], neighborResources['count']))
        
        print('-----------------------')
        
        
        for i in range(len(self.knowledge)):
            sen = self.knowledge[i]
            sen.mark_safe(cell) # remove cell from all sen in KB
            try:
                for mine in sen.known_mines():
                    self.mines.add(mine) # this will add any inferred mines to our mines set
                    
            except TypeError:
                pass # if there are no known mines then it will throw a type error so we can just pass
            
            try:
                for safe in sen.known_safes():
                    self.safes.add(safe) # this will add any inferred safes to our safes set
                
            except TypeError:
                pass # if there are no known safes or mines then it will throw a type error so we can just pass
            
            try:
                for mine in self.mines:
                    sen.mark_mine(mine) # removes any known mines from our sentences
            except TypeError:
                pass
            
        
        # perge updated knowledge base of any empty sentences and safe/mine sentences
        
        for i in range(len(self.knowledge)):
        
            sen = self.knowledge[i]
            print('In perge loop')
            print(len(self.knowledge))
            print(sen)
            print('-----------------')
            
            if sen.count == 0:
                for cell in sen.cells:
                    self.safes.add(cell)
                del self.knowledge[i]
                break
            if len(sen.cells) == sen.count:
                self.mines.add(cell)
                del self.knowledge[i]
                break
            if not bool(vars(sen)):
                del self.knowledge[i]
                break

        # loop over knowledge and see if any of the sentences are subsets of each other
        

        
        KBcopy = copy.deepcopy(self.knowledge)
        while len(KBcopy) > 0:
            print('In subset loop')
            sen1 = KBcopy.pop()
            print(len(KBcopy))
            print(sen1)
            print('-----------------')
            if len(sen1.cells) == 0 or sen1.count == 0:
                pass
            else:
                for sen2 in KBcopy:
                    if sen1.cells.issubset(sen2.cells):
                        newCells = sen2.cells - sen1.cells
                        newCount = sen2.count - sen1.count
                        if len(newCells) != 0:
                            newSen = Sentence(newCells, newCount)
                            if newSen not in self.knowledge: 
                                self.knowledge.append(newSen)
                    elif sen2.cells.issubset(sen1.cells):
                        newCells = sen1.cells - sen2.cells
                        newCount = sen1.count - sen2.count
                        if len(newCells) != 0:
                            newSen = Sentence(newCells, newCount)
                            if newSen not in self.knowledge: 
                                self.knowledge.append(newSen)
                    else: 
                        pass        
            


    def make_safe_move(self):
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        # check to see if there are any cells that are marked in safes that are not marked in moves made
        for cell in self.safes:
            if cell not in self.moves_made:
                return cell
        # loop over knowledge and see if any sentances have a count of 0 if so we can return a cell from that sentence that hasnt been moved to, updating the sentence would be updating the kb tho so return and dont update???
        for sentence in self.knowledge:
            print(sentence)
            if sentence.count == 0:
                for cell in sentence.cells:
                    if cell not in self.moves_made:
                        return cell

        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # will likely cause horrible luck and get me trapped in an infinite loop but send it
        while True:
            i = random.randint(0, self.height - 1)
            j = random.randint(0, self.width - 1)
            if (i, j) not in self.moves_made and (i, j) not in self.mines:
                return (i, j)
            else:
                return None
