import os
from skimage import io
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TWILLIO_SID = os.environ.get('TWILLIO_SID', '')
TWILLIO_AUTH_TOKEN  = os.environ.get('TWILLIO_AUTH_TOKEN', '')
TO_NUMBER = os.environ.get('TO_NUMBER')
FROM_NUMBER = os.environ.get('FROM_NUMBER')
CAM_CONFIG = [
    {
        'name': 'Cypress',
        'url': 'http://snowstakecam.cypressmountain.com/axis-cgi/jpg/image.cgi?resolution=1024x768',
        'stake_roi': ((25, 600), (600, 700)),
        'white_threshold': 0.6,
        'cm_to_y_map': {
                5: 10,
                10: 60,
                15: 107,
                20: 158,
                25: 213,
                30: 273,
                35: 333,
                40: 395,
            },
    },
    {
        'name': 'Whistler',
        'url': 'http://common.snow.com/mtncams/wbsnowstake.jpg',
        'stake_roi': ((200, 1200), (530, 700)),
        'white_threshold': 0.7,
        'cm_to_y_map': {
            5: 110,
            10: 155,
            15: 200,
            20: 248,
            25: 295,
            30: 345,
            35: 395,
            40: 450,
        }
    }
]

def get_roi(img, y_offset, height=10):
    """Get the roi using a y offset
    """
    img_height = img.shape[0]
    y_min = img_height - y_offset
    y_max = y_min + height
    return img[y_min:y_max, :]


def img_has_snow(img, threshold):
    avg_color = img.mean()

    # if the mean value of the roi is greater than the threshold
    # then we can be fairly certain that it has snowed up to that point
    if avg_color >= threshold:
        return True
    return False


def check_cam(cam_data):
    # fetch the most recent image from the web
    img = io.imread(cam_data['url'], as_grey=True)

    # crop the image to only look at the snow stake
    stake_roi = cam_data['stake_roi']
    snow_stake_img = img[stake_roi[0][0]:stake_roi[0][1], stake_roi[1][0]:stake_roi[1][1]]

    # the cm_to_y_map below maps the height in centimeters marked on the snow stake
    # to the pixel location in the y-axis where that mark is in the image
    cm_to_y_map = data['cm_to_y_map']

    snow_height = 0  # cm
    for height_cm in sorted(cm_to_y_map.keys()):
        y_offset = cm_to_y_map[height_cm]
        roi = get_roi(img, y_offset)
        if img_has_snow(roi, cam_data['white_threshold']):
            snow_height = height_cm

    return snow_height


result = {}
for data in CAM_CONFIG:
    result[data['name']] = check_cam(data)

messages = []
for name, snow_height in result.items():
    if snow_height:
        messages.append('It snowed {}cm overnight at {}!'.format(snow_height, name.title()))

if messages:
    msg = '\n'.join(messages)
    print(msg)

    if TWILLIO_SID and TWILLIO_AUTH_TOKEN:
        client = Client(TWILLIO_SID, TWILLIO_AUTH_TOKEN)
        message = client.messages.create(
            to=TO_NUMBER,
            from_=FROM_NUMBER,
            body=msg
        )

