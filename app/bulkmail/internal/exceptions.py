class BulkmailException(Exception):
    ...


class RepositoryException(BulkmailException):
    ...


class SaveMessageError(RepositoryException):
    ...


class SaveBulkmailError(RepositoryException):
    ...


class EmptyBulkmailError(BulkmailException):
    ...
