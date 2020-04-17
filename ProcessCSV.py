import requests
import Properties
import logging
import csv

# Set logging level
logging.basicConfig(level=logging.INFO, filename='./pricing.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%m-%d %H:%M'
                    )

shopifyURL = Properties.shopifyURL
# Go to Google Sheets, File>Publish to Web and publish the sheet as a csv
sheetsURL = Properties.sheetsURL
# Headers need to contain your access token and declare json content type 'X-Shopify-Access-Token': 'YOURS', 'Content-type':'application/json'
headers = {'X-Shopify-Access-Token': '33d82f7196b2d95dec06f5129729aaee', 'Content-type':'application/json'}

logging.info("Getting pricing.")
with requests.Session() as s:
    download = s.get(sheetsURL)

    decoded_content = download.content.decode('utf-8')

    cr = csv.reader(decoded_content.splitlines(), delimiter=',')

    for row in cr:
        if row[2] == "VariantId":
            continue
        if len(row[4]) == 0:
            continue
        price = row[4]
        variantId = row[2]
        productName = row[0]
        productVendor = row[1]

        variantPutData = '{"variant": {"price": "' + price + '","compare_at_price":""}}'

        variantUrl = shopifyURL + variantId + ".json"
        logging.info("Attempting to update price for product: " + productName + " vendor: " + productVendor)
        putPrice = requests.put(variantUrl, data=variantPutData.encode('utf-8'), headers=headers)
        if putPrice.status_code == 200:
            logging.info("Success: Updated price for product: " + productName + " vendor: " + productVendor)
            logging.info("Price is now: " + price)
        if putPrice.status_code != 200:
            logging.error("Unable to update price for product: " + productName + " vendor: " + productVendor)
            logging.error(putPrice.status_code)
            logging.error(putPrice.reason)
            logging.error(putPrice.content)

