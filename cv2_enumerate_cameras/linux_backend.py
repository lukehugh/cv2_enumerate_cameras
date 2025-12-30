from cv2_enumerate_cameras.camera_info import CameraInfo
import os
import glob
import ctypes
import fcntl


try:
    import cv2
    CAP_GSTREAMER = cv2.CAP_GSTREAMER
    CAP_V4L2 = cv2.CAP_V4L2
except ModuleNotFoundError:
    CAP_GSTREAMER = 1800
    CAP_V4L2 = 200


supported_backends = (CAP_GSTREAMER, CAP_V4L2)


# struct v4l2_capability (videodev2.h)
class v4l2_capability(ctypes.Structure):
    _fields_ = [
        ("driver", ctypes.c_char * 16),
        ("card", ctypes.c_char * 32),
        ("bus_info", ctypes.c_char * 32),
        ("version", ctypes.c_uint),
        ("capabilities", ctypes.c_uint),
        ("device_caps", ctypes.c_uint),
        ("reserved", ctypes.c_uint * 3),
    ]


# VIDIOC_QUERYCAP (videodev2.h)
VIDIOC_QUERYCAP = 0x80685600

# V4L2_CAP_VIDEO_CAPTURE (videodev2.h)
V4L2_CAP_VIDEO_CAPTURE = 0x00000001


def read_line(*args):
    try:
        with open(os.path.join(*args), encoding='utf-8', errors='replace') as f:
            line = f.readline().strip()
        return line
    except IOError:
        return None


def device_can_capture_video(path):
    capability = v4l2_capability()
    try:
        with open(path, 'rb', buffering=0) as fd:
            fcntl.ioctl(fd, VIDIOC_QUERYCAP, capability)
    except OSError:
        # If we can't check device info, assume it supports capture
        return True
    return capability.device_caps & V4L2_CAP_VIDEO_CAPTURE


def cameras_generator(apiPreference):
    for path in glob.glob('/dev/video*'):
        # find device name and index
        device_name = os.path.basename(path)
        if not device_name[5:].isdigit():
            continue
        index = int(device_name[5:])

        # check if device supports video capture
        if not device_can_capture_video(path):
            continue

        # read camera name
        video_device_path = f'/sys/class/video4linux/{device_name}'
        video_device_name_path = os.path.join(video_device_path, 'name')
        if os.path.exists(video_device_name_path):
            name = read_line(video_device_name_path)
        else:
            name = device_name

        # find vendor id and product id
        vid = None
        pid = None
        usb_device_path = os.path.join(video_device_path, 'device')
        if os.path.exists(usb_device_path):
            usb_device_path = os.path.realpath(usb_device_path)

            if ':' in os.path.basename(usb_device_path):
                usb_device_path = os.path.dirname(usb_device_path)

            vid = read_line(usb_device_path, 'idVendor')
            pid = read_line(usb_device_path, 'idProduct')
            if vid is not None:
                vid = int(vid, 16)
            if pid is not None:
                pid = int(pid, 16)

        yield CameraInfo(index, name, path, vid, pid, apiPreference)


__all__ = ['supported_backends', 'cameras_generator']
