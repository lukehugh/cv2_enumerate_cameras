import re

import AVFoundation

from cv2_enumerate_cameras.camera_info import CameraInfo

try:
    import cv2

    CAP_AVFOUNDATION = cv2.CAP_AVFOUNDATION
except ModuleNotFoundError:
    CAP_AVFOUNDATION = 1200

supported_backends = (CAP_AVFOUNDATION,)


def cameras_generator(apiPreference):
    _VID_RE = re.compile(r"VendorID_(\d+)")
    _PID_RE = re.compile(r"ProductID_(\d+)")

    # macOS hardware connection notifications are delivered asynchronously via the NSRunLoop.
    # Running it once is enough to process pending notifications and update the list.
    run_loop = AVFoundation.NSRunLoop.currentRunLoop()
    run_loop.runUntilDate_(AVFoundation.NSDate.dateWithTimeIntervalSinceNow_(0)) # runs loop once

    # Use AVCaptureDeviceDiscoverySession if available (macOS 10.15+).
    if hasattr(AVFoundation, "AVCaptureDeviceDiscoverySession"):
        device_types = [
            AVFoundation.AVCaptureDeviceTypeBuiltInWideAngleCamera,
            AVFoundation.AVCaptureDeviceTypeExternalUnknown,
        ]

        # Explicitly add Continuity Camera if available (macOS 13.0+)
        if hasattr(AVFoundation, "AVCaptureDeviceTypeContinuityCamera"):
            device_types.append(AVFoundation.AVCaptureDeviceTypeContinuityCamera)

        device_discovery_session = AVFoundation.AVCaptureDeviceDiscoverySession
        discovery_session = device_discovery_session.discoverySessionWithDeviceTypes_mediaType_position_(
            device_types,
            AVFoundation.AVMediaTypeVideo,
            AVFoundation.AVCaptureDevicePositionUnspecified,
        )
        devs = discovery_session.devices()
    else:
        # Fallback for older macOS versions (pre-10.15)
        devs = AVFoundation.AVCaptureDevice.devicesWithMediaType_(
            AVFoundation.AVMediaTypeVideo
        )
        devs = devs.arrayByAddingObjectsFromArray_(
            AVFoundation.AVCaptureDevice.devicesWithMediaType_(
                AVFoundation.AVMediaTypeMuxed
            )
        )

    devs = list(devs)

    devs.sort(key=lambda d: d.uniqueID())

    for i, d in enumerate(devs):
        model = str(d.modelID())
        vid_m = _VID_RE.search(model)
        pid_m = _PID_RE.search(model)

        yield CameraInfo(
            index=i,
            name=d.localizedName(),
            path=d.uniqueID(),  # macOS does not provide a path, but uniqueID persists with a device over time
            vid=int(vid_m.group(1)) if vid_m else None,
            pid=int(pid_m.group(1)) if pid_m else None,
            backend=apiPreference,
        )


__all__ = ["supported_backends", "cameras_generator"]
