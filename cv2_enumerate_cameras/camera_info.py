try:
    import cv2
    CAP_ANY = cv2.CAP_ANY
except ModuleNotFoundError:
    CAP_ANY = 0


class CameraInfo:
    __slots__ = 'index', 'name', 'path', 'vid', 'pid', 'backend'

    def __init__(self, index, name, path, vid, pid, backend):
        self.index = index
        self.name = name
        self.path = path
        self.vid = vid
        self.pid = pid
        self.backend = backend

    def __str__(self):
        if self.vid is not None and self.pid is not None:
            return f'{self.index}: {self.name} ({self.vid:04X}:{self.pid:04X})'
        return f'{self.index}: {self.name}'

    def __repr__(self):
        return f'{self.__class__.__name__}(index={self.index}, name={self.name!r}, path={self.path!r}, vid={self.vid}, pid={self.pid}, backend={self.backend})'


__all__ = ['CameraInfo']
