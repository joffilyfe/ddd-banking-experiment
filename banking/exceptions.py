class DoesNotExist(Exception):
    """Should be raised when an entity is not found in a datastore.
    
    This exception is not recoverable."""