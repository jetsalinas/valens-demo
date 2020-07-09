import sqlite3


"""
Represents a car object implemented as a
doubly linked list with sublists for cars
of the same color
"""
class Car():

    def __init__(self, id=None, name=None, color=None, left=None, right=None, leftcolor=None, rightcolor=None):
        self.id = id
        self.name = name
        self.color = color
        self.left = left
        self.right = right
        self.leftcolor = leftcolor
        self.rightcolor = rightcolor


"""
Database controller for the cars table
"""
class Controller():


    def __init__(self, conn):
        self.conn = conn


    def close(self):
        self.conn = None


    def create_table(self):

        exec = """CREATE TABLE cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(5) UNIQUE NOT NULL,
            color VARCHAR(255) NOT NULL,
            left INTEGER,
            right INTEGER,
            leftcolor INTEGER,
            rightcolor INTEGER
        );
        """

        c = self.conn.cursor()

        try:
            c.execute(exec)
            self.conn.commit()
        except sqlite3.IntegrityError as e:
            print("INFO: Table cars already exists.")


    """
    Insers a car a the end of the linked list
    """
    def add_car(self, car):

        c = self.conn.cursor()

        c.execute("SELECT * FROM cars WHERE right IS NULL;")
        tail = c.fetchone()

        c.execute("SELECT * FROM cars WHERE rightcolor IS NULL AND color=?;", (car.color,))
        tail_color = c.fetchone()

        if tail is None:

            args = (car.name, car.color, None, None, None, None)
            c.execute("INSERT INTO cars (name, color, left, right, leftcolor, rightcolor) VALUES(?, ?, ?, ?, ?, ?)", args)
            self.conn.commit()
            
            return

        if tail_color is None:
            
            args = (car.name, car.color ,tail[0] ,None ,None ,None)

            c.execute("UPDATE cars SET right=? WHERE right IS NULL;", (tail[0] + 1,))
            c.execute("INSERT INTO cars (name, color, left, right, leftcolor, rightcolor) VALUES(?, ?, ?, ?, ?, ?)", args)
            self.conn.commit()
            
            return


        args = (car.name, car.color, tail[0], None, tail_color[0], None)

        c.execute("UPDATE cars SET right=? WHERE right IS NULL;", (tail[0] + 1,))
        c.execute("UPDATE cars SET rightcolor=? WHERE color=? AND rightcolor IS NULL;", (tail[0] + 1, car.color))
        c.execute("INSERT INTO cars (name, color, left, right, leftcolor, rightcolor) VALUES (?, ?, ?, ?, ?, ?);", args)
        self.conn.commit()


    """
    Returns all the cars in order.
    """
    def get_all(self):

        c = self.conn.cursor()

        c.execute("SELECT * FROM cars WHERE left IS NULL;")
        head = c.fetchone()
        current = head
        res = []

        while current != None:
            res.append(current)
            c.execute("SELECT * FROM cars WHERE left=?;", (current[0], ))
            current = c.fetchone()

        cars = [Car(*r).__dict__ for r in res]
        
        return cars


    """
    Returns all of the cars of a specified color

    color (str): The color to get
    """
    def get_color(self, color):

        c = self.conn.cursor()

        c.execute("SELECT * FROM cars WHERE color=? AND leftcolor IS NULL;", (color,))
        head = c.fetchone()
        current = head
        res = []

        while current:
            res.append(current)
            c.execute("SELECT * FROM cars WHERE id=?", (current[6],))
            current = c.fetchone()

        cars = [Car(*r).__dict__ for r in res]

        return cars


    """
    Deletes a car from the list.

    id (int): The id of the target car
    """
    def pop(self, id):

        c = self.conn.cursor()

        # Update direct neighbors

        c.execute("SELECT * FROM cars WHERE id=?", (int(id),))
        target = c.fetchone()

        if target is None:
            return None, "ERROR: No such target ID exists"

        car = Car(*target)

        c.execute("SELECT * FROM cars WHERE id=?;", (target[3],))
        left = c.fetchone()

        c.execute("SELECT * FROM cars WHERE id=?;", (target[4],))
        right = c.fetchone()

        if (left is None) and (right is None):
            return car, "ERROR: There is only one car"

        if (left is None) and (right is not None):
            c.execute("UPDATE cars SET left=? WHERE id=?;", (None, right[0]))
        
        if (right is None) and (left is not None):
            c.execute("UPDATE cars SET right=? WHERE id=?;", (None, left[0]))

        if (left is not None) and (right is not None):
            c.execute("UPDATE cars SET left=? WHERE id=?;", (left[0], right[0]));
            c.execute("UPDATE cars SET right=? WHERE id=?", (right[0], left[0]))

        # Update color neighbors

        c.execute("SELECT * FROM cars WHERE id=?;", (target[5],))
        leftcolor = c.fetchone()

        c.execute("SELECT * FROM cars WHERE id=?", (target[6],))
        rightcolor = c.fetchone()

        if (leftcolor is None) and (rightcolor is not None):
            c.execute("UPDATE cars SET leftcolor=? WHERE id=?;", (None, rightcolor[0]))

        if (rightcolor is None) and (leftcolor is not None):
            c.execute("UPDATE cars SET rightcolor=? WHERE id=?;", (None, leftcolor[0]))

        if (leftcolor is not None) and (rightcolor is not None):
            c.execute("UPDATE cars SET leftcolor=? WHERE id=?;", (leftcolor[0], rightcolor[0]))
            c.execute("UPDATE cars SET rightcolor=? WHERE id=?;", (rightcolor[0], leftcolor[0]))

        c.execute("DELETE FROM cars WHERE id=?;", (target[0],))

        return car, "SUCCESS"


    """
    Inserts a car after the specified index.
    Use zero to insert a car at the head

    car (Car)
    t (int)
    """
    def insert(self, car, t):

        # TODO: Implement handling of case where
        # there is only one node

        c = self.conn.cursor()

        if t == 0:
            c.execute("SELECT * FROM cars WHERE left IS NULL;")
            head = c.fetchone()
            
            c.execute("SELECT * FROM cars WHERE color=? AND leftcolor IS NULL;", (car.color,))
            head_color = c.fetchone()

            c.execute("UPDATE cars SET left=? WHERE id=?;", (car.id, head[0]))
            c.execute("UPDATE cars SET leftcolor=? WHERE color=? AND leftcolor IS NULL;", (car.id, car.color))

            args = (car.id, car.name, car.color, None, head[0], None, head_color[0])
            c.execute("INSERT INTO cars (id, name, color, left, right, leftcolor, rightcolor) VALUES (?, ?, ?, ?, ?, ?, ?);", args)

            return car, "SUCCESS"

        else:
            c.execute("SELECT * FROM cars WHERE id=?;", (t,))
            target = c.fetchone()

            if target is None:
                return None, "ERROR: Target index does not exist."

            c.execute("SELECT * FROM cars WHERE id=?;", (target[4],))
            target_right = c.fetchone()

            c.execute("UPDATE cars SET right=? WHERE id=?;", (car.id, target[0]))
            car.left = target[0]

            if target_right is not None:
                c.execute("UPDATE cars SET left=? WHERE id=?;", (car.id, target_right[0]))
                car.right = target_right[0]

            current = target
            while current:
                if current[2] == car.color:
                    c.execute("UPDATE cars SET rightcolor=? WHERE id=?;", (car.id, current[0]))
                    car.leftcolor = current[0]
                c.execute("SELECT * FROM cars WHERE right=?;", (current[0],))
                current = c.fetchone()

            if target_right:
                current = target
                while current:
                    if current[2] == car.color:
                        c.execute("UPDATE cars SET leftcolor=? WHERE id=?;", (car.id, current[0]))
                        car.rightcolor = current[0]
                    c.execute("SELECT * FROM cars WHERE left=?;", (current[0],))
                    current = c.fetchone()

            args = (car.id, car.name, car.color, car.left, car.right, car.leftcolor, car.rightcolor)

            c.execute("INSERT INTO cars (id, name, color, left, right, leftcolor, rightcolor) VALUES (?, ?, ?, ?, ?, ?, ?);", args)

            return car, "SUCCESS";