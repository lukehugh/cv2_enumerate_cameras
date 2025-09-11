<div align="center">

# cv2_enumerate_cameras

![PyPI - Version](https://img.shields.io/pypi/v/cv2-enumerate-cameras)
![Python Version from PEP 621 TOML](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fchinaheyu%2Fcv2_enumerate_cameras%2Fmain%2Fpyproject.toml)
![PyPI - Downloads](https://img.shields.io/pypi/dm/cv2-enumerate-cameras)

Retrieve camera's name, VID, PID, and the corresponding OpenCV index.

![](https://raw.githubusercontent.com/chinaheyu/cv2_enumerate_cameras/main/assets/script.png)

</div>

## Installation

### Install from PyPI

```commandline
pip install cv2_enumerate_cameras
```

### Install from Source

```commandline
pip install git+https://github.com/chinaheyu/cv2_enumerate_cameras.git
```

## Example

### Run as Script

We have provided a simple script that prints out information for all cameras. Open a shell and simply run:

```commandline
python -m cv2_enumerate_cameras
```

### Supported Backends

Since OpenCV supports many different backends, not all of them provide support for camera enumeration. The following code demonstrates how to retrieve the names of the supported backends.

```python
from cv2.videoio_registry import getBackendName
from cv2_enumerate_cameras import supported_backends

for backend in supported_backends:
    print(getBackendName(backend))
```

Currently supported backends on windows:

- Microsoft Media Foundation (CAP_MSMF)
- DirectShow (CAP_DSHOW)

Currently supported backends on linux:

- GStreamer (CAP_GSTREAMER)
-  V4L/V4L2 (CAP_V4L2)

Currently supported backends on macOS:

- AVFoundation (CAP_AVFOUNDATION)

### Enumerate Cameras

This is an example showing how to enumerate cameras.

```python
from cv2_enumerate_cameras import enumerate_cameras

for camera_info in enumerate_cameras():
    print(f'{camera_info.index}: {camera_info.name}')
```

The `enumerate_cameras(apiPreference: int = CAP_ANY)` function comes with the default parameter `CAP_ANY`, and you will receive output similar to the following:

```
1400: HD Webcam
...
700: HD Webcam
701: OBS Virtual Camera
...
```

These indices may seem strange, since [opencv defaults to using the high digits of index to represent the backend](https://github.com/opencv/opencv/blob/43112409ef0b711b18c2dc12433ad5e2403aea71/modules/videoio/src/cap.cpp#L384). For example, 701 indicates the second camera on the DSHOW backend (700).

You can also select a supported backend for enumerating camera devices.

Here's an example of enumerating camera devices via the `CAP_MSMF` backend on windows.

```python
import cv2
from cv2_enumerate_cameras import enumerate_cameras

for camera_info in enumerate_cameras(cv2.CAP_MSMF):
    print(f'{camera_info.index}: {camera_info.name}')
```

Output:

```
0: HD Webcam
...
```

Once you have found the target camera, you can create a `cv2.VideoCapture` by its **index** and **backend** properties.

```pycon
cap = cv2.VideoCapture(camera_info.index, camera_info.backend)
```

When using `CAP_ANY` as an option for the `enumerate_cameras` function, the backend parameter can be omitted. However, it is highly recommended to pass it along when creating a `VideoCapture`.

### Camera Info

The `cv2_enumerate_cameras.enumerate_cameras()` function will return a list of `CameraInfo` objects, each containing information about a specific camera.

```pycon
def enumerate_cameras(apiPreference: int = CAP_ANY) -> list[CameraInfo]:
    ...
```

- `CameraInfo.index`: Camera index for creating `cv2.VideoCapture`;
- `CameraInfo.name`: Camera name;
- `CameraInfo.path`:  Camera device path;
- `CameraInfo.vid`:  Vendor identifier;
- `CameraInfo.pid`:  Product identifier;
- `CameraInfo.backend`: Camera backend.

### Find Camera by Vendor and Product Identifier

This example demonstrates how to automatically select a camera based on its VID and PID and create a `VideoCapture` object.

```python
import cv2
from cv2_enumerate_cameras import enumerate_cameras

# define a function to search for a camera
def find_camera(vid, pid, apiPreference=cv2.CAP_ANY):
    for i in enumerate_cameras(apiPreference):
        if i.vid == vid and i.pid == pid:
            return cv2.VideoCapture(i.index, i.backend)
    return None

# find the camera with VID 0x04F2 and PID 0xB711
cap = find_camera(0x04F2, 0xB711)

# read and display the camera frame
while True:
    result, frame = cap.read()
    if not result:
        break
    cv2.imshow('frame', frame)
    if cv2.waitKey(1) == ord('q'):
        break
```

## TODO

Pull requests are very welcome.

- [x] Windows Support
- [x] Linux Support
- [x] MacOS Support (Experimental)
