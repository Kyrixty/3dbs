"""
Models used for 3D Battleship. Used throughout other modules in the application.
"""

class Board:
    """Not really a board, is it?"""
    def __init__(self, owner, x: int, y: int, z: int): #dimensions
        self.owner = owner
        self.x = x
        self.y = y
        self.z = z
        self.ships = []
        self.SetupBoard()
    
    def __repr__(self):
        return f"OWNER: {self.owner} :: \"{self.owner.name}\"\nFront: {self.Front}\nSide: {self.Side}\nTop: {self.Top}\nXYZ:{self.x, self.y, self.z}"
    
    def SetupBoard(self) -> None:
        """
        Sets up top, front and side grids.
        """
        self.Top = [[0]*self.x]*self.z
        self.Front = [[0]*self.x]*self.y
        self.Side = [[0]*self.z]*self.y
    
    def CreateShip(self, x: int, y: int, z: int, size: int, is_vertical: bool) -> bool:
        """
        Used to create ships that will be inserted into the game.

        Please use this method instead of initializing ships on their own as they
        will not be added to the game that way.
        """

        if self.owner: #This board must have an owner. Initialization was not done correctly if it does not.
            ship = Ship(len(self.ships), self.owner, x, y, z, size, is_vertical)
            topCells = ship.GetTopCells()
            frontCells = ship.GetFrontCells()
            sideCells = ship.GetSideCells()
            resetCells = False

            """
            TODO: Continue to test ship intersection checks & ship out of bounds checks.

            NOTE: Ship intersection & ship out of bounds checks have not been tested thoroughly.
            While the checks *should* work, please report any bugs if and when you find them.
            """

            for cell in topCells:
                try:
                    if self.Top[cell[1]][cell[0]] == 0: #Cell is not already occupied.
                        self.Top[cell[1]][cell[0]] = [ship, False] #Cell is returned as [x, z] however in order to access that cell we need to index the row (z) first, then index the cell/column (x).
                    else: #Cell is already occupied, therefore we must set resetCells to True as the ship cannot be created as it intersects with another ship.
                        resetCells = True
                except IndexError:
                    resetCells = True #Ship goes out of bounds, thus an incorrect origin+size+orientation combination was provided for this board.
            for cell in frontCells:
                try:
                    if self.Front[cell[1]][cell[0]] == 0: #Cell is not already occupied.
                        self.Front[cell[1]][cell[0]] = [ship, False] #Cell is returned as [x, y] however in order to access that cell we need to index the row (y) first, then index the cell/column (x).
                    else: #Cell is already occupied, therefore we must set resetCells to True as the ship cannot be created as it intersects with another ship.
                        resetCells = True
                except IndexError:
                    resetCells = True #Ship goes out of bounds, thus an incorrect origin+size+orientation combination was provided for this board.
            for cell in sideCells:
                try:
                    if self.Side[cell[1]][cell[0]] == 0: #Cell is not already occupied
                        self.Side[cell[1]][cell[0]] = [ship, False] #Cell is returned as [z, y] however in order to access that cell we need to index the row (y) first, then index the cell/column (z).
                    else: #Cell is already occupied, therefore we must set resetCells to True as the ship cannot be created as it intersects with another ship.
                        resetCells = True
                except IndexError:
                    resetCells = True #Ship goes out of bounds, thus an incorrect origin+size+orientation combination was provided for this board.
            
            if not resetCells: #Adding the ship to the board was successful
                self.ships.append(ship)
            else: #Ship either goes out of bounds of the board or intersects with another ship.
                self.ResetCells(topCells, frontCells, sideCells)
                return False
            return True
        else: #Board has no owner, thus it was not initialized correctly.
            raise Exception("No owner exists for this board. Did you forget to specify the owner of this board during initialization?")
    
    def CreateShot(self) -> None: ...
    
    def ResetCells(self, topCells: list, frontCells: list, sideCells: list) -> None:
        """
        Resets given cells.
        """
        for cell in topCells:
            self.Top[cell[1]][cell[0]] = 0
        for cell in frontCells:
            self.Front[cell[1]][cell[0]] = 0
        for cell in sideCells:
            self.Side[cell[1]][cell[0]] = 0

class Player:
    """
    Basic player class. Documentation provided
    with methods themselves, not here.
    """

    def __init__(self, playerName: str, maxShips: int):
        self.name = playerName
        self.maxShips = maxShips
        self.ships = []
    
    def SetupPlayer(self) -> None: ...

class Ship:
    """
    A ship is in this case a target for a player to hit.
    
    **PLEASE DO NOT CREATE SHIPS WITH ``Ship(*args)``, THIS IS
    NOT HOW THE BOARD EXPECTS THEM TO BE CREATED. INSTEAD,
    INITIALIZE A BOARD OBJECT AND USE IT'S ``CreateShip()``
    METHOD!**
    """

    def __init__(self, ship_id: int, owner: Player, x: int, y: int, z: int, 
                size: int, is_vertical: bool, debug=False):
        """
        Owner is expected to be an object of ``Player`` type.\n
        ``is_vertical`` is True if the ship is vertical from the 
        top view, False if otherwise.
        """
        self.id = ship_id
        self.owner = owner
        self.x = x
        self.y = y
        self.z = z
        self.size = size
        self.health = size
        self.is_vertical = is_vertical
        if debug:
            self.run_tests()
    
    def GetTopCells(self) -> list:
        """
        Calculates the cells that this ship occupies in the top grid.
        Usage: GetTopCells()
        Grid: X*Z
        """
        return self.get_remaining_cells(self.x, self.z, "TOP")

    def GetFrontCells(self) -> list:
        """
        Calculates the cells that this ship occupies in the front grid.
        Usage: GetFrontCells()
        Grid: X*Y
        """
        return self.get_remaining_cells(self.x, self.y, "FRONT")

    def GetSideCells(self) -> list:
        """
        Calculates the cells that this ship occupies in the side grid.
        Usage: GetSideCells()
        Grid: Z*Y
        """
        return self.get_remaining_cells(self.z, self.y, "SIDE")
    
    def get_remaining_cells(self, origin_ind: int, origin_dep: int, mode: str) -> list:
        """
        Gets remaining cells given origin independant, origin dependant & mode (top, front, side).
        It does this by using python's version of a switch case statement which--although awkward--keeps
        the code clean and readable.
        Please note it isn't necessary to understand how any of this works, just know that it does and
        should correctly calculate which cells are going to be occupied by this ship.
        """
        MODES = { #set up switch statement.
            True: { #vertical
                "TOP": self.get_top_at_vertical,
                "FRONT": self.get_front_at_vertical,
                "SIDE": self.get_side_at_vertical
            },
            False: { #not vertical
                "TOP": self.get_top_at_non_vertical,
                "FRONT": self.get_front_at_non_vertical,
                "SIDE": self.get_side_at_non_vertical
            }
        }

        return MODES[self.is_vertical][mode](origin_ind, origin_dep, self.size) #This is pretty much python's version of a switch case statement.
    
    def get_top_at_vertical(self, x: int, z: int, size: int) -> list:
        """
        Get top cells where ``is_vertical`` is True. The reason that you
        call ``GetTopCells()`` instead of this function is the fact that
        ``get_remaining_cells()`` determines what mode we're currently in.
        """
        origin = [x, z]
        cells = [origin]

        for i in range(size-1): #Since we already have the origin, size must be subtracted by 1.
            z += 1
            cells.append([x, z])
        
        return cells
    
    def get_top_at_non_vertical(self, x: int, z: int, size: int) -> list:
        """
        Get top cells where ``is_vertical`` is False. The reason that you
        call ``GetTopCells()`` instead of this function is the fact that
        ``get_remaining_cells()`` determines what mode we're currently in.
        """
        origin = [x, z]
        cells = [origin]

        for i in range(size-1): #Since we already have the origin, size must be subtracted by 1.
            x += 1
            cells.append([x, z])
        
        return cells
    
    def get_front_at_vertical(self, x: int, y: int, size: int) -> list:
        """
        Get front cells where ``is_vertical`` is True. The reason that you
        call ``GetFrontCells()`` instead of this function is the fact that
        ``get_remaining_cells()`` determines what mode we're currently in.
        """
        return [[x, y]] #Will be just a point, therefore occupies only 1 cell on the front view.
    
    def get_front_at_non_vertical(self, x: int, y: int, size: int) -> list:
        """
        Get front cells where ``is_vertical`` is False. The reason that you
        call ``GetFrontCells()`` instead of this function is the fact that
        ``get_remaining_cells()`` determines what mode we're currently in.
        """
        origin = [x, y]
        cells = [origin]

        for i in range(size-1): #Since we already have the origin, size must be subtracted by 1.
            x += 1
            cells.append([x, y])
        
        return cells
    
    def get_side_at_vertical(self, z: int, y: int, size: int) -> list:
        """
        Get side cells where ``is_vertical`` is True. The reason that you
        call ``GetSideCells()`` instead of this function is the fact that
        ``get_remaining_cells()`` determines what mode we're currently in.
        """
        origin = [z, y]
        cells = [origin]

        for i in range(size-1): #Since we already have the origin, size must be subtracted by 1.
            z += 1
            cells.append([z, y])
        
        return cells
    
    def get_side_at_non_vertical(self, z: int, y: int, size: int) -> list:
        """
        Get side cells where ``is_vertical`` is False. The reason that you
        call ``GetSideCells()`` instead of this function is the fact that
        ``get_remaining_cells()`` determines what mode we're currently in.
        """
        return [[z, y]] #Will just be a point, therefore only occupies one cell on the side view.
    
    def run_tests(self) -> bool:
        """
        Calls specific methods.
        """
        try:
            print(self.GetTopCells())
            print(self.GetFrontCells())
            print(self.GetSideCells())
            return True
        except:
            return False

class BaseShot:
    """
    Base shot class. Can be used to create more
    complex shots through inheritance.
    """
    def __init__(self, shot_origin: list, is_vertical: bool,
                 board_x: int, board_y: int, board_z: int):
        """
        ``shot_origin`` is expected to be a list of 3 elements regarding it's origin (e.g. ["XY", 5, 4]).\n
        ``is_vertical`` is expected to be a boolean which tells us whether or not the shot
        was fired horizontally or vertically. ``is_vertical`` is True if the shot direction
        is vertical when viewed from the top view, False if otherwise.
        """
        self.origin = shot_origin
        self.topCells = []
        self.frontCells = []
        self.sideCells = []
        self.is_vertical = is_vertical
        self.boardX, self.boardY, self.boardZ = board_x, board_y, board_z

    def __repr__(self):
        return f"Top: {self.topCells}\nFront: {self.frontCells}\nSide: {self.sideCells}"

    def CreateRay(self) -> None:
        """
        Using ``origin`` and ``is_vertical``,
        calculate the cells this shot will
        occupy in the top, front, and side
        views.

        Since the ``Ship`` class already has
        methods that can do this, we will
        simply reuse them here.
        Top: x*z
        Front: x*y
        Side: z*y
        """
        Shot = None
        if "XZ" in self.origin: #Top
            size = self.DetermineAppropriateSize("TOP")
            Shot = Ship(0, "Shot", self.origin[1], self.boardY-1, self.origin[2], size, self.is_vertical) #Y = MAX(Y) (max possible value of Y)
        elif "XY" in self.origin: #Front
            size = self.DetermineAppropriateSize("FRONT")
            Shot = Ship(0, "Shot", self.origin[1], self.origin[2], 0, size, self.is_vertical) #Z = 0
        else: #Side (shown as "ZY")
            size = self.DetermineAppropriateSize("SIDE")
            Shot = Ship(0, "Shot", self.boardX-1, self.origin[2], self.origin[1], size, self.is_vertical) #X = MAX(X) (max possible value of X)
        
        self.topCells = Shot.GetTopCells()
        self.frontCells = Shot.GetFrontCells()
        self.sideCells = Shot.GetSideCells()
    
    def DetermineAppropriateSize(self, view: str) -> int:
        """
        Handles determining the appropriate size,
        as well as also determining whether or not
        the shot should be vertical when fired from
        the front or side view.
        """
        size = 0
        if view=="TOP":
            if self.is_vertical:
                size = self.boardZ #Size of ray is equal to the board's Z value.
            else:
                size = self.boardX #Size of ray is equal to the board's X value.
        elif view=="FRONT":
            size = self.boardX #It wouldn't make sense to fire vertically on the Front view. Only the top view.
            self.is_vertical = False #If a shot is fired from the front view, is_vertical must be False.
        else: #Side
            size = self.boardZ #Size of ray is equal to the board's Z value.
            self.is_vertical = True #If a shot is fired from the side view, is_vertical must be True.
        return size #It is worthy to note that since it is pointless to fire vertically from the front and side views, the size of the ray will never be equal to the board's Y value.

"""
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
These are tests that you can try to see if everything is working. Copy
the test's source code and paste it into the bottom of the file to run the test.

NOTE: The results may be out of date, please update them if they are.
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
=========================================================================
TEST 01
-------
s = BaseShot(["ZY", 0, 2], True, 4, 4, 4)
s.CreateRay()
print(s)

-> RESULT:
Top: [[3, 0], [3, 1], [3, 2], [3, 3]]
Front: [[3, 2]]
Side: [[0, 2], [1, 2], [2, 2], [3, 2]]
=========================================================================
"""