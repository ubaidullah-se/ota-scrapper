from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
from time import sleep
import pandas as pd
import os


def setup_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    # If you not want to images to load uncomment the following line
    # options.add_argument("--blink-settings=imagesEnabled=false")

    # loading my custom extension, which I made for proxy rotation
    options.add_argument("--load-extension=./extensions/proxy-rotator")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)

    return driver


def scrape_hotel_urls(driver, main_url):
    driver.get(main_url)

    # Wait for JavaScript rendering
    wait = WebDriverWait(driver, 100)

    wait.until(
        EC.element_to_be_clickable(
            (
                By.CSS_SELECTOR,
                "[data-stid=section-results] .uitk-button.uitk-button-secondary",
            )
        )
    )

    sleep(5)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")

    hotel_urls = []
    hotel_elements = driver.find_elements(
        By.CSS_SELECTOR, "a.uitk-card-link[data-stid=open-hotel-information]"
    )

    for hotel in hotel_elements:
        url = hotel.get_attribute("href")
        hotel_urls.append(url)

    return hotel_urls


def scrape_hotel_data(driver, hotel_url):
    driver.get(hotel_url)

    wait = WebDriverWait(driver, 100)
    wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "div[data-stid=section-room-list]")
        )
    )

    rooms = []

    hotel_name = None
    try:
        hotel_name = driver.find_element(
            By.CSS_SELECTOR, "div[data-stid=standout-stays-card] h1.uitk-heading"
        ).text
    except:
        hotel_name = driver.find_element(
            By.CSS_SELECTOR, "div[data-stid=content-hotel-title] h1.uitk-heading"
        ).text

    location = driver.find_element(
        By.CSS_SELECTOR, "div[data-stid=content-hotel-address]"
    ).text

    room_elements = driver.find_elements(
        By.CSS_SELECTOR, "div[data-stid=section-room-list]>div>div"
    )
    for room in room_elements:
        room_type = room.find_element(By.CSS_SELECTOR, "h3.uitk-heading-6").text

        original_price = None
        discounted_price = None
        try:
            original_price = room.find_element(
                By.CSS_SELECTOR, "div[data-test-id=price-summary-message-line] del"
            ).text
            discounted_price = room.find_element(
                By.CSS_SELECTOR, "div[data-test-id=price-summary-message-line] span"
            ).text
        except:
            try:
                original_price = room.find_element(
                    By.CSS_SELECTOR, "div[data-test-id=price-summary-message-line] span"
                ).text
            except:
                original_price = "sold out"

        room_features = room.find_elements(By.CSS_SELECTOR, ".uitk-typelist li")
        room_features = " | ".join(list(map(lambda item: item.text, room_features)))

        rooms.append(
            {
                "hotel_name": hotel_name,
                "location": location,
                "room_type": room_type,
                "features": room_features,
                "original_price": original_price,
                "discounted_price": discounted_price,
            }
        )

    return rooms


def main(destination=""):
    print("starting browser...")
    main_url = f"https://www.hotels.com/Hotel-Search?destination={destination}"

    driver = setup_driver()
    try:
        print("scrapping hotel urls...")
        hotel_urls = scrape_hotel_urls(driver, main_url)
        print("hotels found:", len(hotel_urls))
    except Exception as e:
        print(f"Error scraping main page: {e}")
        driver.quit()
        return

    file_name = f"data/{datetime.now()}.csv"
    for index, hotel_url in enumerate(hotel_urls):
        try:
            print("scrapping hotel no", index + 1)
            hotel_data = scrape_hotel_data(driver, hotel_url)
            df = pd.DataFrame(hotel_data)
            df.to_csv(
                file_name,
                mode="a",
                sep="\t",
                header=not os.path.exists(file_name),
                index=False,
            )

        except Exception as e:
            print(f"Error scraping {hotel_url}: {e}")

    print("all data saved in:", file_name)
    driver.quit()


if __name__ == "__main__":
    main(destination="Tokyo Japan")
