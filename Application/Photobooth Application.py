from flask import Flask, request, url_for, render_template, Response
import PySpin
import ctypes
import numpy as np
import cv2
from streamer_pkg.streamer import Streamer


lib_ici = ctypes.WinDLL('icisdk_x64.dll')


# Obtain image from ICI camera
def get_ici_image():
    # Creates Camera Method
    init_cam = lib_ici['StartCamera']
    init_cam.restype = ctypes.c_int
    init_cam.argtypes = [ctypes.c_int]
    # Creates Dimension Methods
    get_img_width = lib_ici['GetImgWidth']
    get_img_width.restype = ctypes.c_int
    get_img_height = lib_ici['GetImgHeight']
    get_img_height.restype = ctypes.c_int
    # Creates Image Acquisition Method
    get_raw_image = lib_ici['GetRawImage']
    get_raw_image.restype = ctypes.POINTER(ctypes.c_uint16)
    # Creates Kill Method
    kill_cam = lib_ici['StopCamera']
    kill_cam.restype = None

    # Camera Initialization
    init_cam(0)
    w = get_img_width()
    h = get_img_height()
    buffer_size = w * h * ctypes.sizeof(ctypes.c_uint16)

    # Constants
    resize = (600, 480)
    ratio = 1.25
    height_zoom = 10
    width_zoom = int(height_zoom * ratio)

    # Obtain Image
    ir_frame = get_raw_image()
    ir_data = ctypes.cast(ir_frame, ctypes.POINTER(ctypes.c_uint16 * buffer_size))
    ir_img_data = np.ndarray(buffer=ir_data.contents, dtype=np.uint16, shape=(h, w))
    # Conversion to 8-Bit RGB Colormap
    ir_img_min = ir_img_data.min()
    ir_img_max = ir_img_data.max()
    ir_img_normalized = ((ir_img_data - ir_img_min) * (255 / (ir_img_max - ir_img_min))).astype(np.uint8)
    ici = cv2.applyColorMap(ir_img_normalized, cv2.COLORMAP_JET)
    # Image Resizing
    ici_size = [ici.shape[0], ici.shape[1]]
    ici_ratio = round(ici.shape[1] / ici.shape[0], 2)
    while ici_ratio != ratio:
        ici_ratio = round(ici_size[1] / ici_size[0], 2)
        if ici_ratio > ratio:
            ici_size[1] -= 5
        elif ici_ratio < ratio:
            ici_size[0] -= 5
    ici_crop = [int((480 - ici_size[0]) / 2), int((640 - ici_size[1]) / 2)]
    cropped_ici = ici[ici_crop[0]:ici.shape[0] - ici_crop[0], ici_crop[1]:ici.shape[1] - ici_crop[1]]
    # Zoomed to account for slight depth difference in camera positions
    zoomed_ici = cropped_ici[height_zoom:cropped_ici.shape[0] - height_zoom,
                 width_zoom:cropped_ici.shape[1] - width_zoom]
    resized_ici = cv2.resize(zoomed_ici, resize)

    return resized_ici


# Obtain image from Flir camera
def get_flir_image():
    # Initialize system and camera
    system = PySpin.System.GetInstance()
    cam_list = system.GetCameras()
    cam = cam_list.GetByIndex(0)
    cam.Init()
    # Setting frame rate
    nodemap = cam.GetNodeMap()
    frame_rate_enable = PySpin.CBooleanPtr(nodemap.GetNode('AcquisitionFrameRateEnable'))
    if PySpin.IsAvailable(frame_rate_enable) and PySpin.IsWritable(frame_rate_enable):
        frame_rate_enable.SetValue(True)

        frame_rate = PySpin.CFloatPtr(nodemap.GetNode('AcquisitionFrameRate'))
        if PySpin.IsAvailable(frame_rate) and PySpin.IsWritable(frame_rate):
            frame_rate.SetValue(10)

    # Constants
    resize = (600, 480)
    ratio = 1.25

    # Obtain Image
    image = cam.GetNextImage()
    converted_image = image.Convert(PySpin.PixelFormat_BGR8, PySpin.HQ_LINEAR)
    flir = converted_image.GetNDArray()
    image.Release()
    # Image Resizing
    flir_size = [flir.shape[0], flir.shape[1]]
    flir_ratio = round(flir.shape[1] / flir.shape[0], 2)
    while (flir_ratio != ratio):
        flir_ratio = round(flir_size[1] / flir_size[0], 2)
        if flir_ratio > ratio:
            flir_size[1] -= 5
        elif flir_ratio < ratio:
            flir_size[0] -= 5
    flir_crop = [int((flir.shape[0] - flir_size[0]) / 2), int((flir.shape[1] - flir_size[1]) / 2)]
    cropped_flir = flir[flir_crop[0]:flir.shape[0] - flir_crop[0], flir_crop[1]:flir.shape[1] - flir_crop[1]]
    resized_flir = cv2.resize(cropped_flir, resize)
    cam.EndAcquisition()
    cam.DeInit()
    del cam
    cam_list.Clear()
    system.ReleaseInstance()

    return resized_flir


# Obtain combined ICI and Flir Image
def get_combined_image():
    ici = get_ici_image()
    flir = get_flir_image()
    offset = 70
    vl_middle = int(flir.shape[1] / 2)
    ir_middle = vl_middle + offset
    full_img = np.hstack((flir[0:, 0:vl_middle], ici[0:, ir_middle:]))
    return full_img


app = Flask(__name__)


@app.route('/')
def home():
    return render_template('Home.html')


@app.route('/video')
def video():
    port = 5001
    require_login = False
    streamer = Streamer(port, require_login)

    cam = cv2.VideoCapture(cv2.CAP_DSHOW)

    while True:
        ret, frame = cam.read()
        streamer.update_frame(frame)

        if not streamer.is_streaming:
            streamer.start_streaming()

    cam.release()

    return render_template('Live Feed.html')


@app.route('/contacts')
def contact_info():
    return render_template('Contact Info.html')
    print('Yeah')


@app.route('/print')
def print_or_dig():
    return render_template('Print.html')


if __name__ == '__main__':
    app.run(debug = True)
