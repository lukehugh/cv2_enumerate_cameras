<div align="center">

# cv2_enumerate_cameras

![PyPI - Version](https://img.shields.io/pypi/v/cv2-enumerate-cameras)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fchinaheyu%2Fcv2_enumerate_cameras%2Fmain%2Fpyproject.toml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/cv2-enumerate-cameras)

Retrieve camera names, VID/PID information, device paths, and the corresponding OpenCV indices.

![](https://raw.githubusercontent.com/chinaheyu/cv2_enumerate_cameras/main/assets/script.png)

</div>

## Installation

### Install from PyPI

```commandline
pip install cv2-enumerate-cameras
```

## Quick Start

### Run as a Script

A simple command-line script is provided to enumerate all cameras:

```commandline
lscam
```

Or run the module directly:

```commandline
python -m cv2_enumerate_cameras
```

### Integrate into Your Project

To enumerate cameras inside your code:

```python
from cv2_enumerate_cameras import enumerate_cameras

for camera_info in enumerate_cameras():
    print(camera_info)
```

By default, `enumerate_cameras()` is called with the parameter `CAP_ANY`, which instructs `cv2_enumerate_cameras` to probe all supported backends when enumerating cameras. Example output:

```
1400: 2K USB Camera (2BDF:02A5)
700: 2K USB Camera (2BDF:02A5)
701: OBS Virtual Camera
```

These seemingly unusual indices are intentional: [OpenCV encodes the backend ID into the high digits of the index](https://docs.opencv.org/4.12.0/d8/dfe/classcv_1_1VideoCapture.html#aabce0d83aa0da9af802455e8cf5fd181). For example, 701 indicates the second camera (1) on the DSHOW backend (700).

To explicitly use a specific backend:

```python
import cv2
from cv2_enumerate_cameras import enumerate_cameras

for camera_info in enumerate_cameras(cv2.CAP_MSMF):
    print(camera_info)
```

Output:

```
0: 2K USB Camera (2BDF:02A5)
1: ...
2: ...
```

Once you have found the target camera, you can create a `cv2.VideoCapture` by its **index** and **backend** properties.

```pycon
cap = cv2.VideoCapture(camera_info.index, camera_info.backend)
```

When using `CAP_ANY`, the backend argument can be omitted. But for robust behavior, explicitly passing it is strongly recommended.

## Supported Backends

Not all OpenCV backends support camera enumeration. Use the following snippet to print the names of the supported backends:

```python
from cv2.videoio_registry import getBackendName
from cv2_enumerate_cameras import supported_backends

for backend in supported_backends:
    print(getBackendName(backend))
```

Windows:

- Microsoft Media Foundation (`CAP_MSMF`)
- DirectShow (`CAP_DSHOW`)

Linux:

- GStreamer (`CAP_GSTREAMER`)
-  V4L/V4L2 (`CAP_V4L2`)

macOS:

- AVFoundation (`CAP_AVFOUNDATION`)

## CameraInfo Object

`enumerate_cameras()` returns a list of `CameraInfo` objects:

```pycon
def enumerate_cameras(apiPreference: int = CAP_ANY) -> list[CameraInfo]:
    ...
```

- `CameraInfo.index`: Camera index for the selected backend
- `CameraInfo.name`: Human-readable device name
- `CameraInfo.path`:  Device path (macOS: `uniqueID`);
- `CameraInfo.vid`:  USB Vendor ID (if available);
- `CameraInfo.pid`:  USB Product ID (if available);
- `CameraInfo.backend`: OpenCV backend used for enumeration.

## Examples

### Automatically Select a Camera by VID/PID

This example finds a camera using VID/PID and creates a `VideoCapture`:

```python
import cv2
from cv2_enumerate_cameras import enumerate_cameras

# Search for a specific camera by VID and PID
def find_camera(vid, pid, apiPreference=cv2.CAP_ANY):
    for i in enumerate_cameras(apiPreference):
        if i.vid == vid and i.pid == pid:
            return cv2.VideoCapture(i.index, i.backend)
    raise RuntimeError('Camera not found!')

# Example: Find the camera with VID 0x04F2 and PID 0xB711
cap = find_camera(0x04F2, 0xB711)

# Capture and display frames
while True:
    ok, frame = cap.read()
    if not ok:
        break
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break
```
