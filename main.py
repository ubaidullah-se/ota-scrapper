from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime
import pandas as pd
import os


def setup_driver():
    """Sets up and returns a Chrome WebDriver with specified options."""
    options = webdriver.ChromeOptions()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--load-extension=./extensions/proxy-rotator")

    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def scrape_hotel_urls(driver, main_url):
    """Scrapes and returns a list of hotel URLs from the main hotel search page."""
    driver.get(main_url)
    wait = WebDriverWait(driver, 100)

    try:
        wait.until(
            EC.element_to_be_clickable(
                (
                    By.CSS_SELECTOR,
                    "[data-stid=section-results] .uitk-button.uitk-button-secondary",
                )
            )
        )
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
        hotel_elements = driver.find_elements(
            By.CSS_SELECTOR, "a.uitk-card-link[data-stid=open-hotel-information]"
        )
        return [hotel.get_attribute("href") for hotel in hotel_elements]
    except Exception as e:
        print(f"Error scraping hotel URLs: {e}")
        return []


def scrape_hotel_data(driver, hotel_url):
    """Scrapes and returns data for a single hotel given its URL."""
    driver.get(hotel_url)
    wait = WebDriverWait(driver, 100)

    try:
        wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div[data-stid=section-room-list]")
            )
        )
        hotel_name = extract_hotel_name(driver)
        location = driver.find_element(
            By.CSS_SELECTOR, "div[data-stid=content-hotel-address]"
        ).text

        rooms = extract_rooms(driver)
        return [
            {"hotel_name": hotel_name, "location": location, **room} for room in rooms
        ]
    except Exception as e:
        print(f"Error scraping hotel data: {e}")
        return []


def extract_hotel_name(driver):
    """Extracts and returns the hotel name."""
    try:
        return driver.find_element(
            By.CSS_SELECTOR, "div[data-stid=standout-stays-card] h1.uitk-heading"
        ).text
    except:
        return driver.find_element(
            By.CSS_SELECTOR, "div[data-stid=content-hotel-title] h1.uitk-heading"
        ).text


def extract_rooms(driver):
    """Extracts and returns a list of room data for the current hotel page."""
    room_elements = driver.find_elements(
        By.CSS_SELECTOR, "div[data-stid=section-room-list]>div>div"
    )
    rooms = []
    for room in room_elements:
        room_type = room.find_element(By.CSS_SELECTOR, "h3.uitk-heading-6").text
        original_price, discounted_price = extract_prices(room)

        room_features = room.find_elements(By.CSS_SELECTOR, ".uitk-typelist li")
        room_features = " | ".join([feature.text for feature in room_features])

        rooms.append(
            {
                "room_type": room_type,
                "features": room_features,
                "original_price": original_price,
                "discounted_price": discounted_price,
            }
        )
    return rooms


def extract_prices(room):
    """Extracts and returns the original and discounted prices for a room."""
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
            discounted_price = None
        except:
            original_price = "sold out"
            discounted_price = None

    return original_price, discounted_price


def save_data(hotel_data, file_name):
    """Saves hotel data to a CSV file."""
    df = pd.DataFrame(hotel_data)
    df.to_csv(
        file_name,
        mode="a",
        sep="\t",
        header=not os.path.exists(file_name),
        index=False,
    )


def main(destination="Tokyo Japan"):
    print("Starting browser...")
    main_url = f"https://www.hotels.com/Hotel-Search?destination={destination}"

    driver = setup_driver()
    try:
        print("Scraping hotel URLs...")
        hotel_urls = scrape_hotel_urls(driver, main_url)
        print(f"Hotels found: {len(hotel_urls)}")
    except Exception as e:
        print(f"Error scraping main page: {e}")
        driver.quit()
        return

    file_name = f"data/{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    for index, hotel_url in enumerate(hotel_urls):
        try:
            print(f"Scraping hotel {index + 1} of {len(hotel_urls)}")
            hotel_data = scrape_hotel_data(driver, hotel_url)
            if hotel_data:
                save_data(hotel_data, file_name)
        except Exception as e:
            print(f"Error scraping {hotel_url}: {e}")

    print(f"All data saved in: {file_name}")
    driver.quit()


if __name__ == "__main__":
    main()
