import os
import distro
import platform
import subprocess
import random
import time
import logging
import random
from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from threading import Lock
lock = Lock()
c = 0

with open("proxies.txt", "r") as file:
    proxy_pool_list = [proxy.strip() for proxy in file.readlines()[10:]]


def setup_logging():
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )


def connection_status(driver):
    global c
    if wait_for_element_exists(driver, By.XPATH, "//*[text()='Connected']"):
        c += 1
        logging.info(f"Status: Connected! [{c}]")
        return True
    elif wait_for_element_exists(driver, By.XPATH, "//*[text()='Disconnected']"):
        logging.warning("Status: Disconnected!")
        return False
    else:
        logging.warning("Status: Unknown!")
        return None

def check_active_element(driver):
    try:
        wait_for_element(driver, By.XPATH, "//*[text()='Activated']")
        driver.find_element(By.XPATH, "//*[text()='Activated']")
        logging.info("Extension is activated!")
    except NoSuchElementException:
        logging.error(
            "Failed to find 'Activated' element. Extension activation failed."
        )


def wait_for_element_exists(driver, by, value, timeout=30):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return True
    except TimeoutException:
        return False


def wait_for_element(driver, by, value, timeout=15):
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((by, value))
        )
        return element
    except TimeoutException as e:
        logging.error(f"Error waiting for element {value}: {e}")
        # raise
        pass


def set_local_storage_item(driver, key, value):
    driver.execute_script(f"localStorage.setItem('{key}', '{value}');")
    result = driver.execute_script(f"return localStorage.getItem('{key}');")
    return result


def add_cookie_to_local_storage(driver, cookie_value):
    keys = ["np_webapp_token", "np_token"]
    for key in keys:
        result = set_local_storage_item(driver, key, cookie_value)
        logging.info(
            f"Added {key} with value {result[:8]}...{result[-8:]} to local storage."
        )
    logging.info("!!!!! Your token can be used to login for 7 days !!!!!")


# def get_chromedriver_version():
#     try:
#         result = subprocess.run(
#             ["chromedriver", "--version"], capture_output=True, text=True
#         )
#         return result.stdout.strip()
#     except Exception as e:
#         logging.error(f"Could not get ChromeDriver version: {e}")
#         return "Unknown version"


def get_os_info():
    try:
        os_info = {"System": platform.system(), "Version": platform.version()}

        if os_info["System"] == "Linux":
            os_info.update(
                {
                    "System": distro.name(pretty=True),
                    "Version": distro.version(pretty=True, best=True),
                }
            )
        return os_info
    except Exception as e:
        logging.error(f"Could not get OS information: {e}")
        return "Unknown OS"

#NOTE
# def interceptor(request):
#     # Block PNG, JPEG and GIF images
#     if request.path.endswith(('.png', '.jpg', '.gif')):
#         request.abort()


def intercept(request):
    # print(f"Captured request [intercept]: {request.url}")
    # Check if the URL contains 'googleapis.com' and block those requests
    if request.path.endswith(('.png', '.jpg', '.gif', '.svg')):
        request.abort()
    if 'googleapis.com' in request.url or 'update.googleapis.com' in request.url:
        logging.info(f"Blocking request to: {request.url}")
        request.abort()  # Abort the request
    # Check if the URL matches the Google API and block it
    if 'optimizationguide-pa.googleapis.com' in request.url:
        logging.info(f"Blocking request to: {request.url}")
        request.abort()  # Block the request
    if ('svg' in request.url or 'jpg' in request.url) and 'nodepay' in request.url:
        logging.info(f"Blocking request to: {request.url}")
        request.abort()  # Block the request
    if 'gravatar.com' in request.url:
        logging.info(f"Blocking request to: {request.url}")
        request.abort()  # Block the request
    if 'googletagmanager.com' in request.url:
        logging.info(f"Blocking request to: {request.url}")
        request.abort()  # Block the request
    if 'google-analytics.com' in request.url:
        logging.info(f"Blocking request to: {request.url}")
        request.abort()  # Block the request
    if 'content-autofill.googleapis.com' in request.url:
        logging.info(f"Blocking request to: {request.url}")
        request.abort()  # Block the request
    if 'edgedl.me.gvt1.com' in request.url:
        logging.info(f"Blocking request to: {request.url}")
        request.abort()  # Block the request
    if '/static/media/' in request.url:
        logging.info(f"Blocking request to: {request.url}")
        request.abort()  # Block the request

def run(proxy):
    global c
    setup_logging()

    branch = ""
    version = "1.0.9" + branch
    secUntilRestart = 60
    logging.info(f"Started the script {version}")

    try:
        os_info = get_os_info()
        logging.info(f"OS Info: {os_info}")

        # Read variables from the OS env
        cookie = os.getenv("NP_COOKIE")
        extension_id = os.getenv("EXTENSION_ID")
        extension_url = os.getenv("EXTENSION_URL")

        # Check if credentials are provided
        if not cookie:
            logging.error(
                "No cookie provided. Please set the NP_COOKIE environment variable."
            )
            return  # Exit the script if credentials are not provided

        # Check the operating system
        if platform.system() == "Linux":
            chromedriver_path = "/usr/bin/chromedriver"
            service = Service(chromedriver_path)
        else:
            service = None  # On Windows or other OS, no need to set chromedriver path

        chrome_options = Options()
        chrome_options.add_extension(f"./{extension_id}.crx")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument(
            "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0"
        )

        # Use proxy if provided
        seleniumwire_options = {}
        if proxy:
            seleniumwire_options = {
                "proxy": {
                    "http": proxy,
                    "https": proxy,
                    "no_proxy": "localhost,127.0.0.1",  # Disable proxy for localhost
                },
                'exclude_hosts':[
                    'googleapis.com',
                    'optimizationguide-pa.googleapis.com',
                    'gravatar.com',
                    'googletagmanager.com',
                    'google-analytics.com',
                    'update.googleapis.com',
                    'content-autofill.googleapis.com',
                    'www.googletagmanager.com',
                    'accounts.google.com',
                    'edgedl.me.gvt1.com',
                    'www.googleapis.com',
                    'www.optimizationguide-pa.googleapis.com',
                    'www.gravatar.com',
                    'www.googletagmanager.com',
                    'www.google-analytics.com',
                    'www.update.googleapis.com',
                    'www.content-autofill.googleapis.com',
                    ]
                }

        # Initialize the WebDriver
        # chromedriver_version = get_chromedriver_version()
        # logging.info(f"Using {chromedriver_version}")
        with lock:
            if service:
                driver = webdriver.Chrome(service=service,
                options=chrome_options, seleniumwire_options=seleniumwire_options
            )
            else:
                driver = webdriver.Chrome(
                options=chrome_options, seleniumwire_options=seleniumwire_options
            )

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error(f"Restarting in 60 seconds...")
        driver.quit()
        time.sleep(secUntilRestart)
        run(random.choice(proxy_pool_list))
        # c -= 1
        # logging.error(f"An error occurred: {e}")
        # logging.error(f"Restarting in {secUntilRestart} seconds...")
        # logging.error(f"Close Connection.")
        # driver.quit()
        return

    try:
        driver.request_interceptor = intercept
        # NodePass checks for width less than 1024p
        driver.set_window_size(1024, driver.get_window_size()["height"])

        # Navigate to a webpage
        logging.info(f"Navigating to {extension_url} website...")
        with lock:
            driver.get(extension_url)
        time.sleep(random.randint(7, 12))
        with lock:
            add_cookie_to_local_storage(driver, cookie)
        time.sleep(random.randint(2, 6))

        # # Check successful login
        # while not wait_for_element_exists(driver, By.XPATH, "//*[text()='Dashboard']"):
        #     logging.info(
        #         f"Refreshing in {secUntilRestart} seconds to check login (If stuck, verify your token)..."
        #     )
        #     with lock:
        #         driver.get(extension_url)

        # logging.info("Logged in successfully!")

        time.sleep(random.randint(3, 7))
        logging.info("Accessing extension settings page...")
        with lock:
            driver.get(f"chrome-extension://{extension_id}/index.html")
        time.sleep(random.randint(12, 20))
        with lock:
            driver.refresh()
            time.sleep(random.randint(10, 15))
        # Refresh until the "Login" button disappears

        # while wait_for_element_exists(driver, By.XPATH, "//*[text()='Login']"):
        #     logging.info("Clicking the extension login button...")
        #     login = driver.find_element(By.XPATH, "//*[text()='Login']")
        #     with lock:
        #         login.click()
        #     time.sleep(10)
            # Refresh the page
            # driver.refresh()

        # Check for the "Activated" element
        # check_active_element(driver)

        # Get handles for all windows
        all_windows = driver.window_handles

        # Get the handle of the active window
        active_window = driver.current_window_handle

        # Close all windows except the active one
        with lock:
            for window in all_windows:
                if window != active_window:
                    driver.switch_to.window(window)
                    driver.close()

            # Switch back to the active window
            driver.switch_to.window(active_window)

            if connection_status(driver) == None:
                raise
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        logging.error(f"Restarting in {secUntilRestart} seconds...")
        # logging.error(f"Close Connection.")
        driver.quit()
        time.sleep(secUntilRestart)
        run(random.choice(proxy_pool_list))
        return

    while True:
        try:
            logging.info(f'Connected proxies: {c}')
            time.sleep(3600)
            with lock:
                driver.refresh()
            # while connection_status(driver) == None:
            #     logging.info("Attemt to reconnect...")
            #     c += 1
            #     driver.refresh()
            #     time.sleep(60)
            #     if connection_status(driver):
            #         break
            #     if c > 5:
            #         logging.info("Stopping the script due atempts failure...")
            #         driver.quit()
            #         return

        except KeyboardInterrupt:
            logging.info("Stopping the script...")
            driver.quit()
            break


with open("proxies.txt", "r") as file:
    proxy_list = [proxy.strip() for proxy in file.readlines()[:10]]
    # print(proxy_list)


# def define_proxy(proxy):
    # host, port, username, password = proxy.split(":")
    # proxy_url = f"http://{username}:{password}@{host}:{port}"
    # return proxy


# proxies = [define_proxy(proxy) for proxy in proxy_list]

from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor(max_workers=len(proxy_list)) as pool:
    pool.map(run, proxy_list)
