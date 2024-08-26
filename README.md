# OTA Scraper

**OTA**: Hotels.com  
**URL**: [Hotels.com - Japan](https://www.hotels.com/Hotel-Search?destination=Japan)  
**Python**: 3.11

## Setup Instructions

### 1. Create a Virtual Environment

```bash
python -m venv env
```

### 2. Activate the Virtual Environment

```bash
source env/bin/activate
```

### 3. Install Required Packages

```bash
pip install -r requirements.txt
```

### 4. Run the Scraper

```bash
python main.py
```

## Additional Information

### Scraping Process

The scraper first collects basic details of hotels from the main hotel listing page. Based on the assignment's requirements, it then proceeds to scrape room details from each hotel's individual URL one by one. If you only need basic hotel information and not the room details, you can stop the scraper after it collects the initial hotel data.

### Custom Chrome Extension for Proxy Rotation

This scraper uses a custom Chrome browser extension to rotate proxies. The reason for using this extension is that Selenium does not provide an option to update the browser proxy on the fly. Normally, you would have to quit the browser and open it again if you needed to change the proxy. However, by using a Chrome extension, we gain access to deeper APIs, allowing us to change the proxy without restarting the browser.

### Proxy Configuration

The proxies used by the extension are stored in an array in the `./extensions/proxy-rotator/background.js` file. These proxies are my personal proxies, and you can update them if needed.

### Data Storage

The data for each scrape is saved in the `data` folder with the date and time when the scraper was run. The data is appended live during the scraping process, ensuring that no data is lost. Additionally, there are some sample data scrapes available in the `data` folder in CSV format.

### Sample Data Format

The sample data in the `data` folder includes the following fields:

- `hotel_name`
- `location`
- `room_type`
- `features`
- `original_price`
- `discounted_price`

Format:

```
| hotel_name    | location    | room_type | features    | original_price    | discounted_price    |
|---------------|-------------|-----------|-------------|-------------------|---------------------|
| ...           | ...         | ...       | ...         | ...               | ...                 |
|---------------|-------------|-----------|-------------|-------------------|---------------------|
```


### Customizing the Destination

You can update the destination in the main script function to scrape hotels in different locations. Currently, the default destination is set to Tokyo, Japan.
