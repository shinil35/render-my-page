import requests
import json
import base64
import time

from selenium import webdriver
from selenium.webdriver.chrome.options import Options  

backdoor_pwd = '3074bc8c-0a1f-48ae-aedc-54fe9fdd8a32'
base_url = 'http://web:80'

# Load error image
error_image = base64.b64encode(open("error_image.png", "rb").read()).decode('utf-8')

while True:
    # List pages to process
    res = requests.get('%s/bot/page_list.php?backdoor=%s' % (base_url, backdoor_pwd))
    pages = json.loads(res.text)

    for page in pages:
        page_id = int(page['id'])
        user_id = int(page['user_id'])

        print("Processing page %d from user %d" % (page_id, user_id))
        
        # Get a session for this user
        res = requests.get('%s/bot/login_as_bot.php?backdoor=%s&user_id=%d' % (base_url, backdoor_pwd, user_id))
        session = json.loads(res.text)['PHPSESSID']
        print("Got session: %s" % session)

        dummy_page = '%s/empty.php' % (base_url)
        page_url = '%s/page.php?id=%d' % (base_url, page_id)
        cookies = 'PHPSESSID=%s;' % (session)

        image = error_image
        try:
            # Browser setup
            chrome_options = Options()
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--disable-gpu")
            chrome_options.add_argument("--disable-dev-shm-using")
            chrome_options.add_argument("--disable-software-rasterizer")

            driver = webdriver.Chrome(options=chrome_options)
            driver.set_page_load_timeout(5)

            # Inject cookies
            driver.get(dummy_page)
            driver.add_cookie({'name': 'PHPSESSID', 'value': session})

            # Visit page
            driver.get(page_url)

            try:
                # Accept alert if present
                alert = driver.switch_to.alert
                alert.accept()
            except:
                pass

            image = driver.get_screenshot_as_base64()

            driver.close()
        except Exception as e:
            print("Exception while taking screenshot: ")
            print(e)
            pass

        # Upload image or error
        data = {'page_id': page_id, 'image': 'data:image/png;base64,%s' % image}
        res = requests.post('%s/bot/upload_image.php?backdoor=%s' % (base_url, backdoor_pwd), data=data)

        print("Upload status: %s" % res.text)
    
    print()
    time.sleep(1)