class MentaError(Exception):
    pass


class ExpiredError(MentaError):
    pass


class DecryptError(MentaError):
    pass


class BadFormatError(MentaError):
    pass


class BadVersionError(BadFormatError):
    pass
