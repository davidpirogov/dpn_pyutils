from pathlib import Path


#
# file module exceptions
#
class FileOperationError(Exception):
    """ Base class for file exceptions """

    def __init__(self, file_path: Path, message:str):
        self.file_path = file_path
        super().__init__(message)


class FileSaveError(FileOperationError):
    """ Raised when there is an error saving a file """
    pass

class FileOpenError(FileOperationError):
    """ Raised when there is an error opening or reading a file """
    pass

class FileNotFoundError(FileOperationError):
    """ Raised when the specified file has not been found """
    pass



class CryptoError(Exception):
    """ Base class for crypto exceptions """

    def __init__(self, message: str):
        super().__init__(message)

class CryptoInvalidArgumentsError(CryptoError):
    """ Raised when there is are invalid arguments when calling crypto methods """
    pass
