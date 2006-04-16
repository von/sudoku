#!/bin/python
######################################################################
#
# sudoku
#
# Solve sudoku puzzles.
#
######################################################################

debug = False

#
# Constants
#

numRows = 9
numCols = 9
numCells = 9
cellSize = 3
possibleValues = range(1,10)

######################################################################

class Node:
    def __init__(self, x, y, value=None):
        self.x = x
        self.y = y
        self.cellId = int(self.x/cellSize)*cellSize + int(self.y/cellSize)
        if value is None:
            self.anyValue()
        else:
            self.setValue(value)

    def __str__(self):
        if len(self.possibleValues) > 1:
            return "."
        return "%d" % self.value()

    def dump(self):
        if len(self.possibleValues) > 1:
            return str(self.possibleValues)
        return "%d" % self.possibleValues[0]

    def solved(self):
        if len(self.possibleValues) == 1:
            return True
        return False

    def value(self):
        if not self.solved():
            raise Exception("Method value() called for unsolved node.")
        # Make copy of set and pop value. This hack is the only way
        # I see to get at value in set without destruction.
        value = self.possibleValues.copy().pop()
        return value

    def anyValue(self):
        self.possibleValues = set(range(1,10))
        
    def setValue(self, value):
        if debug: print "%d,%d - setting value %d" % (self.x, self.y, value)
        self.possibleValues = set([value])

    def isOption(self, value):
        if value in self.possibleValues:
            return True
        return False
    
    def removeValue(self, value):
        if value not in self.possibleValues:
            return False
        if debug: print "%d,%d - removing %d %s" % (self.x, self.y, value, self.possibleValues)
        self.possibleValues.remove(value)
        if len(self.possibleValues)== 0:
            raise Exception("No legal value for %d,%d" % (self.x, self.y))
        return True
    
    def cellId(self):
        """Return an identifier for the cell of this node."""
        return self.cellId

######################################################################

class Nodes(set):
    """An unordered collection of nodes."""

    def removeValue(self, value):
        """Remove value from all nodes in set."""
        madeChange = False
        for node in self:
            madeChange |= node.removeValue(value)
        return madeChange

    def removeValues(self, values):
        """Remove values from all nodes in set."""
        madeChange = False
        for node in self:
            for value in values:
                madeChange |= node.removeValue(value)
        return madeChange

    def isOption(self, value):
        """Return true if any of nodes have value as possible option."""
        for node in self:
            if node.isOption(value):
                return True
        return False

    def hasValues(self, values):
        """Return nodes that match given set of possible values."""
        matches = Nodes()
        for node in self:
            if node.possibleValues == values:
                matches.add(node)
        return matches

    def hasSubsetOfValues(self, values):
        """Return nodes that match or are a subset of given set of possible values."""
        matches = Nodes()
        for node in self:
            if node.possibleValues.issubset(values):
                matches.add(node)
        return matches

    def hasValue(self, value):
        """Return nodes that have given value."""
        matches = Nodes()
        for node in self:
            if node.isOption(value):
                matches.add(node)
        return matches

    def inRow(self, y):
        """Return true if all nodes are in given row."""
        for node in self:
            if node.y != y:
                return False
        return True

    def inCol(self, x):
        """Return true if all nodes are in given column."""
        for node in self:
            if node.x != x:
                return False
        return True

    def commonRow(self):
        """If all nodes are in the same row, return that row number. Otherwise return None."""
        if len(self) == 0:
            return None
        row = None
        for node in self:
            if row is None:
                row = node.y
            elif node.y != row:
                return None
        return row
    
    def commonCol(self):
        """If all nodes are in the same column, return that column number. Otherwise return None."""
        if len(self) == 0:
            return None
        col = None
        for node in self:
            if col is None:
                col = node.x
            elif node.x != col:
                return None
        return col
    
    def commonCell(self):
        """If all nodes are in the same cell, return that cell id. Otherwise return None."""
        if len(self) == 0:
            return None
        cell = None
        for node in self:
            if cell is None:
                cell = node.cellId
            elif node.cellId != cell:
                return None
        return cell
 
######################################################################

class Sudoku:
    def __init__(self):
        self.grid = []
        for x in range(numCols):
            col = []
            self.grid.append(col)
            for y in range(numRows):
                col.append(Node(x,y))

    def __str__(self):
        s = ""
        for y in range(numRows):
            for x in range(numCols):
                s += str(self.grid[x][y])
            s += "\n"
        return s

    def dump(self):
        for y in range(numRows):
            for x in range(numCols):
                node = self.grid[x][y]
                print "%d,%d %s" % (x, y, node.dump())

    
    def loadFromFile(self, fd):
        for y in range(numRows):
            line = fd.readline()
            if line == "":
                raise Exception("Not enough rows")
            for x in range(numCols):
                char = line[x]
                if char == ".":
                    self.grid[x][y].anyValue()
                elif char.isdigit() and char != "0":
                    self.grid[x][y].setValue(int(char))
                else:
                    raise Exception("Illegal value \"%s\" at row %d col %d" % (char, x,y))

    def node(self, x, y):
        return self.grid[x][y]

    def nodes(self):
        nodes = Nodes()
        for column in self.columns():
            nodes.update(column)
        return nodes
    
    def column(self, x):
        return Nodes(self.grid[x])

    def columns(self):
        cols = []
        for x in range(numRows):
            cols.append(self.column(x))
        return cols
    
    def row(self, y):
        row = Nodes()
        for col in self.grid:
            row.add(col[y])
        return row
    
    def rows(self):
        rows = []
        for y in range(numCols):
            rows.append(self.row(y))
        return rows

    def cell(self, cellId):
        nodes = Nodes()
        cellx = int(cellId/cellSize) * cellSize
        celly = (cellId % cellSize) * cellSize
        for x in range(cellx, cellx + cellSize):
            for y in range(celly, celly + cellSize):
                nodes.add(self.grid[x][y])
        return nodes

    def cells(self):
        cells = []
        for cellId in range(numCells):
            cells.append(self.cell(cellId))
        return cells
    
    def colmates(self, node):
        """Given a node, return all the nodes that coexist in the same column."""
        # Add the whole column and then remove node itself
        mates = Nodes(self.column(node.x))
        mates.remove(node)
        return mates

    def rowmates(self, node):
        """Given a node, return all the nodes that coexist in the same row."""
        # Add the whole row and then remove node
        mates = Nodes(self.row(node.y))
        mates.remove(node)
        return mates

    def cellmates(self, node):
        """Given a node, return all the nodes that coexist in the same cell."""
        mates = self.cell(node.cellId)
        mates.remove(node)
        return mates

    def solve(self):
        """Attempt to solve."""
        iterations = 0
        while True:
            madeChange = False
            iterations += 1
            for node in self.nodes():
                madeChange |= self.processNode(node)
            for cell in self.cells():
                madeChange |= self.processCell(cell)
            for row in self.rows():
                madeChange |= self.processRow(row)
            for col in self.columns():
                madeChange |= self.processColumn(col)
            if madeChange is False:
                break
            print self
        if self.solved():
            print "Solved in %d iterations." % iterations
        else:
            print "Giving up after %d iterations." % iterations

    def processNode(self, node):
        madeChange = False
        rowmates = self.rowmates(node)
        colmates = self.colmates(node)
        cellmates = self.cellmates(node)
        if not node.solved():
            # If this node has a value that is unique among any of its mates,
            # then it must be that value.
            for value in node.possibleValues:
                if ((not rowmates.isOption(value)) or
                    (not colmates.isOption(value)) or
                    (not cellmates.isOption(value))):
                    node.setValue(value)
                    madeChange = True
                    # Next test case will remove this node's value from
                    # any mates
        #
        # If this node is solved, then remove it from any of its mates
        # and return.
        if node.solved():
            madeChange |= rowmates.removeValue(node.value())
            madeChange |= colmates.removeValue(node.value())
            madeChange |= cellmates.removeValue(node.value())
            return madeChange
        #
        # The rest of these checks are only for unsolved nodes.
        #
        # See if N-1 mates have the same set, or a subset, of the possibilities
        # of this node, where N is the number of possibilities of this node.
        # If so, then none of the other mates can have those N values.
        n = len(node.possibleValues)
        for mates in [rowmates, colmates, cellmates]:
            if len(mates) <= n:
                continue
            matches = mates.hasSubsetOfValues(node.possibleValues)
            if len(matches) != (n-1):
                continue
            # Found n-1 matching cells with subset of n values
            # Eliminate those values from other mates.
            nonmatches = mates - matches
            madeChange |= nonmatches.removeValues(node.possibleValues)
        return madeChange

    def processCell(self, nodes):
        madeChange = False
        #
        # If a value only appears with a row or column of the node's cell,
        # then we can remove it from all nodes in that row or column outside
        # the cell.
        for value in possibleValues:
            haveValue = nodes.hasValue(value)
            row = haveValue.commonRow()
            if row:
                others = self.row(row) - haveValue
                madeChange |= others.removeValue(value)
                continue
            col = haveValue.commonCol()
            if col:
                others = self.column(col) - haveValue
                madeChange |= others.removeValue(value)
                continue
        return madeChange

    def processRow(self, nodes):
        madeChange = False
        #
        # If a value only appears with a cell or column of the node's row,
        # then we can remove it from all nodes in that cell or column outside
        # the cell.
        for value in possibleValues:
            haveValue = nodes.hasValue(value)
            cell = haveValue.commonCell()
            if cell:
                others = self.cell(cell) - haveValue
                madeChange |= others.removeValue(value)
                continue
            col = haveValue.commonCol()
            if col:
                others = self.column(col) - haveValue
                madeChange |= others.removeValue(value)
                continue
        return madeChange

    def processColumn(self, nodes):
        madeChange = False
        #
        # If a value only appears with a cell or row of the node's column,
        # then we can remove it from all nodes in that cell or row outside
        # the cell.
        for value in possibleValues:
            haveValue = nodes.hasValue(value)
            cell = haveValue.commonCell()
            if cell:
                others = self.cell(cell) - haveValue
                madeChange |= others.removeValue(value)
                continue
            row = haveValue.commonRow()
            if row:
                others = self.row(row) - haveValue
                madeChange |= others.removeValue(value)
                continue
        return madeChange

    def solved(self):
        """Return true if puzzle is solved."""
        for row in self.grid:
            for node in row:
                if not node.solved():
                    return False
        return True

######################################################################
#
# Main program
#

# Parse commandline

import sys

myname = sys.argv.pop(0)
try:
    filename = sys.argv.pop(0)
except:
    print "Usage: %s <filename>" % myname
    sys.exit(1)

fd = open(filename, "r")

game = Sudoku()
game.loadFromFile(fd)
fd.close()

print game

game.solve()

if debug and not game.solved(): game.dump()

