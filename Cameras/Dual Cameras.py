# Camera Imports
import numpy as np
import ctypes
import cv2
import PySpin

# DLL Import
libICI = ctypes.WinDLL('icisdk_x64.dll')

# Creates Camera
InitCam = libICI['StartCamera']
InitCam.restype = ctypes.c_int
InitCam.argtypes = [ctypes.c_int]

#
GetImgWidth = libICI['GetImgWidth']
GetImgWidth.restype = ctypes.c_int
GetImgHeight = libICI['GetImgHeight']
GetImgHeight.restype = ctypes.c_int

#
GetRawImage = libICI['GetRawImage']
GetRawImage.restype = ctypes.POINTER(ctypes.c_uint16)  #returns pointer

#
KillCam = libICI['StopCamera']
KillCam.restype = None      # 32-bit. 1 for success, 0 for fail

# Camera Setting, Width and Height
InitCam(0)
w = GetImgWidth()
h = GetImgHeight()

#
img = ctypes.POINTER(ctypes.c_uint16)
buffer_size = w * h * ctypes.sizeof(ctypes.c_uint16)

system = PySpin.System.GetInstance()
cam_list = system.GetCameras()
cam = cam_list.GetByIndex(0)

cam.Init()

nodemap = cam.GetNodeMap()

frame_rate_enable = PySpin.CBooleanPtr(nodemap.GetNode('AcquisitionFrameRateEnable'))
if PySpin.IsAvailable(frame_rate_enable) and PySpin.IsWritable(frame_rate_enable):
    frame_rate_enable.SetValue(True)

    frame_rate = PySpin.CFloatPtr(nodemap.GetNode('AcquisitionFrameRate'))
    if PySpin.IsAvailable(frame_rate) and PySpin.IsWritable(frame_rate):
        frame_rate.SetValue(10)

cam.BeginAcquisition()
desired_width = 582  # 582 or 536
desired_height = 462  # 462 or 402
scale = 110
ici_crop = (int((640 - desired_width) / 2), int((480 - desired_height) / 2))
flir_crop = 53  # int((2048 - (2448/1.26))/2)
height_offset = 0
flir_height_crop = int(height_offset * 1.26)
width_offset = 35
while True:
    # /*** Spinnaker Cam ***/

    image = cam.GetNextImage()
    converted_image = image.Convert(PySpin.PixelFormat_BGR8, PySpin.HQ_LINEAR)
    data = converted_image.GetNDArray()
    cropped_data = data[flir_crop + height_offset:2048 - flir_crop + height_offset,
                   flir_height_crop:data.shape[1] - flir_height_crop]
    resized_data = cv2.resize(cropped_data, (desired_width, desired_height))
    image.Release()
    cv2.imshow('Spinnaker Cam', resized_data)

    # /*** ICI Cam ***/

    # Frame From IR Cam
    ir_frame = GetRawImage()
    # Ctypes conversion
    try:
        ir_data = ctypes.cast(ir_frame, ctypes.POINTER(ctypes.c_uint16 * buffer_size))
        ir_img_data = np.ndarray(buffer=ir_data.contents, dtype=np.uint16, shape=(h, w))
    except:
        print('ICI Camera not found')
        break
    # Save Memory
    ir_img_min = ir_img_data.min()
    ir_img_max = ir_img_data.max()
    # Normalizing Image
    ir_img_normalized = ((ir_img_data - ir_img_min) * (255 / (ir_img_max - ir_img_min))).astype(np.uint8)
    img_colormap = cv2.applyColorMap(ir_img_normalized, cv2.COLORMAP_JET)

    ici_cropped = img_colormap[ici_crop[1]:480 - ici_crop[1], ici_crop[0]:]

    height, width, channels = ici_cropped.shape

    try:
        resized = cv2.resize(ici_cropped, (int(width * scale / 100), int(height * scale / 100)))
        resized_height, resized_width, resized_channels = resized.shape
        height_crop = int((resized_height - desired_height) / 2)
        width_crop = int((resized_width - desired_width) / 2)
        reject, split, deny = np.split(resized, [width_crop, resized_width - width_crop], 1)
        destroy, cropped, eradicate = np.split(split, [height_crop, resized_height - height_crop], 0)
    except:
        print('Error')
        continue

    try:
        cv2.namedWindow('ICI Cam', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('ICI Cam', (desired_width, desired_height))
        cv2.imshow('ICI Cam', cropped)
    except:
        print('Error')

    key = cv2.waitKey(1)
    if key == ord('i'):
        scale += 1
        print(scale)
    elif key == ord('k'):
        scale -= 1
        print(scale)
    elif key == ord('p'):
        vl_array = resized_data
        ir_array = cropped
        break
    elif key == ord('q'):
        break

cam.EndAcquisition()
cam.DeInit()
del cam

cam_list.Clear()
system.ReleaseInstance()

cv2.destroyAllWindows()

def face_center(image):
    face_cascade = cv2.CascadeClassifier('C:\\Anaconda3\\Library\\etc\\haarcascades\\haarcascade_frontalface_default.xml')
    smile_cascade = cv2.CascadeClassifier('C:\\Anaconda3\\Library\\etc\\haarcascades\\haarcascade_smile.xml')
    profile_cascade = cv2.CascadeClassifier('C:\\Anaconda3\\Library\\etc\\lbpcascades\\lbpcascade_profileface.xml')
    face_center = 0
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
    face = face_cascade.detectMultiScale(gray, 1.3, 5)
    height = 0
    width = 0
    y_center = 0
    for (x, y, w, h) in face:
        face_center = int(x+w/2)
        width = w
        height = h
        y_center = y
    return face_center, width, height, y_center


middle, width, height, y_center = face_center(vl_array)
if middle == 0:
    print('Face not found')
else:
    aoi_length = 60
    offset = 80
    face_vl = middle
    face_ir = face_vl + offset
    vl_img = vl_array[0:desired_height, 0:face_vl + aoi_length]
    ir_img = ir_array[0:desired_height, face_ir - aoi_length:]
    vl_aoi = vl_img[0:, face_vl - aoi_length:face_vl + aoi_length]
    vl_img = vl_img[0:, 0:face_vl - aoi_length]
    ir_aoi = ir_img[0:, 0:aoi_length * 2]
    ir_img = ir_img[0:, aoi_length * 2:]
    splits = np.arange(0, 121, 1)

    blends = np.linspace(0, 1, len(splits))

    vl_splits = []
    ir_splits = []
    for start, end in zip(splits[0:-1], splits[1:]):
        vl_splits.append(vl_aoi[0:desired_height, start:end])
        ir_splits.append(ir_aoi[0:desired_height, start:end])

    aoi_list = list(range(120))
    for i in range(len(splits) - 1):
        aoi_list[i] = (cv2.addWeighted(vl_splits[i], blends[len(splits) - 1 - i], ir_splits[i], blends[i], 0))

    full_aoi = aoi_list[0]
    for i in range(len(aoi_list) - 1):
        full_aoi = np.hstack((full_aoi, aoi_list[i + 1]))
    full_img = np.hstack((vl_img, full_aoi))
    full_img = np.hstack((full_img, ir_img))

    print('Image Width:', full_img.shape[1])
    print('Image Height:', full_img.shape[0])
    cv2.imshow('Smooth Transition', full_img)
    cv2.imshow('Original VL', vl_array)
    cv2.imshow('Original IR', ir_array)
    cv2.imwrite('Transition Image.png', full_img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

