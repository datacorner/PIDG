__ = "Benoit CAYLA"
__email__ = "benoit@datacorner.fr"
__license__ = "MIT"

class cursorByField(object):
    """ This class aims to use the cursor by using the fields directly
    Args:
        cursor (_type_): SQL cursor
        row (_type_): resultset
    """
    def __init__(self, cursor, row):
        for (attr, val) in zip((d[0] for d in cursor.description), row) :
            setattr(self, attr, val)

    def get(self, attribute):
        try:
            return getattr(self, attribute)
        except:
            return None