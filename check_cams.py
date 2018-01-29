import os
from skimage import io
from twilio.rest import Client
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

TWILLIO_SID = os.environ.get('TWILLIO_SID')
TWILLIO_AUTH_TOKEN  = os.environ.get('TWILLIO_AUTH_TOKEN')
TO_NUMBER = os.environ.get('TO_NUMBER')
FROM_NUMBER = os.environ.get('FROM_NUMBER')
WHITE_THRESHOLD = 0.8

cam_data = [
    {
        'name': 'Cypress',
        'url': 'http://snowstakecam.cypressmountain.com/axis-cgi/jpg/image.cgi?resolution=1024x768',
        'stake_roi': [(25, 600), (600, 700)],
        'cm_to_y_map': {
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
        'stake_roi': [(200,1200), (530,700)],
        'cm_to_y_map': {
            10: 150,  # TODO this has not been calibrated yet
            15: 200,
            20: 248,
            25: 295,
            30: 345,
            35: 395,
            40: 450,
        }
    }
]

result = {}
for data in cam_data:
    # get the latest webcam image from cypress mountain
    url = data['url']
    img = io.imread(url, as_grey=True)

    # crop the image to only look at the snow stake
    stake_roi = data['stake_roi']
    snow_stake_img = img[stake_roi[0][0]:stake_roi[0][1], stake_roi[1][0]:stake_roi[1][1]]
    img_height = snow_stake_img.shape[0]

    snow_height = 0
    # the cm_to_y_map below maps the height in centimeters marked on the snow stake
    # to the pixel location where that mark is in the image
    cm_to_y_map = data['cm_to_y_map']

    for height_cm in sorted(cm_to_y_map.keys()):
        y_lower = img_height - cm_to_y_map[height_cm]

        # offset by 10 pixels to have a range to compute the average on to
        # avoid noise from a small area dominating the result
        y_upper = y_lower + 10

        roi = snow_stake_img[y_lower:y_upper, :]
        avg_color = roi.mean()

        # if the mean value of the roi is greater than the WHITE_THRESHOLD
        # then we can be fairly certain that it has snowed up to that point
        if avg_color >= WHITE_THRESHOLD:
            snow_height = height_cm

    result[data['name']] = snow_height

messages = []
for name, snow_height in result.items():
    if snow_height:
        messages.append('It snowed {}cm overnight at {}!'.format(snow_height, name.title()))

if messages:
    msg = '\n'.join(messages)
    print(msg)

    client = Client(TWILLIO_SID, TWILLIO_AUTH_TOKEN)
    message = client.messages.create(
        to=TO_NUMBER,
        from_=FROM_NUMBER,
        body=msg
    )

