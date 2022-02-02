class BulkmailException(Exception):
    ...


class RepositoryException(BulkmailException):
    ...


class SaveMessageError(RepositoryException):
    ...
