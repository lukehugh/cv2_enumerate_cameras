from cv2_enumerate_cameras.camera_info import CameraInfo
import os
import subprocess


try:
    import cv2
    CAP_GSTREAMER = cv2.CAP_GSTREAMER
    CAP_V4L2 = cv2.CAP_V4L2
except ModuleNotFoundError:
    CAP_GSTREAMER = 1800
    CAP_V4L2 = 200

supported_backends = (CAP_GSTREAMER, CAP_V4L2)


def read_line(*args):
    try:
        with open(os.path.join(*args)) as f:
            line = f.readline().strip()
        return line
    except IOError:
        return None
    
def device_can_capture_video(device_name: str) -> bool:
    try:
        device_info = subprocess.check_output(['v4l2-ctl', f'--device=/dev/{device_name}', '--info'])
    except subprocess.CalledProcessError:
        return True  # If we can't check device info, assume it supports capture

    lines = device_info.decode('utf-8').split('\n')
    capabilities_index = next((index for index, line in enumerate(lines) if line.startswith('\tCapabilities')), None)
    device_caps_index = next((index for index, line in enumerate(lines) if line.startswith('\tDevice Caps')), None)
    if device_caps_index is not None:
        search_index = device_caps_index
    elif capabilities_index is not None:
        search_index = capabilities_index # If device has no specific Device Caps, we can trust it's main capabilities
    else:
        return True  # Device info returns no capabilities listed, assume it supports capture

    for line in lines[search_index:]:
        if 'Video Capture' in line:
            return True
        elif not line.startswith('\t\t'):
            return False  # Next header has been reached, no video capture support

    return False

try:
    from linuxpy.video.device import iter_video_capture_devices

    def capture_files():
        for device in iter_video_capture_devices():
            yield device.PREFIX + str(device.index)
except ImportError:
    import glob

    def capture_files():
        yield from glob.glob('/dev/video*')


def cameras_generator(apiPreference):
    for path in capture_files():
        # find device name and index
        device_name = os.path.basename(path)
        if not device_name[5:].isdigit():
            continue
        index = int(device_name[5:])

        # check if device supports video capture
        if not device_can_capture_video(device_name):
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
