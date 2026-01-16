__version__ = '1.3.3'

from cv2_enumerate_cameras.camera_info import CameraInfo
import platform

system = platform.system()

try:
    import cv2
    CAP_ANY = cv2.CAP_ANY
except ModuleNotFoundError:
    CAP_ANY = 0

if system == 'Windows':
    from cv2_enumerate_cameras.windows_backend import supported_backends, cameras_generator
elif system == 'Linux':
    from cv2_enumerate_cameras.linux_backend import supported_backends, cameras_generator
elif system == 'Darwin':
    from cv2_enumerate_cameras.macos_backend import supported_backends, cameras_generator
else:
    from cv2_enumerate_cameras.opencv_backend import supported_backends, cameras_generator


def enumerate_cameras(apiPreference=CAP_ANY):
    if apiPreference != CAP_ANY and apiPreference not in supported_backends:
        raise NotImplementedError(f"Unsupported backend: {apiPreference}!")

    if apiPreference == CAP_ANY:
        return [CameraInfo(i.index + i.backend, i.name, i.path, i.vid, i.pid, CAP_ANY) for j in supported_backends for i in enumerate_cameras(j)]
    else:
        return list(cameras_generator(apiPreference))


__all__ = ['CameraInfo', 'supported_backends', 'enumerate_cameras']
