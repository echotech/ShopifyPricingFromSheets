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
        # Skip CSV Header Row
        if row[2] == "VariantId":
            continue
        # Skip zero pricing
        if len(row[4]) == 0:
            continue
        csvPrice = row[4]
        variantId = row[2]
        productId = row[3]
        productName = row[0]
        productVendor = row[1]
        logging.info("Attempting to update price for product: " + productName + " vendor: " + productVendor)

        variantGetURL = shopifyURL + variantId + ".json"
        getCurrentPrice = requests.get(variantGetURL, headers=headers)
        currentPriceJson = getCurrentPrice.json()
        currentVariant = currentPriceJson['variant']
        existingPrice = currentVariant['price']

        if ("$" + existingPrice) == csvPrice:
            logging.info("Current price is the same as csv price. Skipping.")
            continue

        variantPutData = '{"variant": {"price": "' + csvPrice + '","compare_at_price":""}}'

        variantUrl = shopifyURL + variantId + ".json"

        putPrice = requests.put(variantUrl, data=variantPutData.encode('utf-8'), headers=headers)
        if putPrice.status_code == 200:
            logging.info("Success: Updated price for product: " + productName + " vendor: " + productVendor)
            logging.info("Price is now: " + csvPrice)
        if putPrice.status_code != 200:
            logging.error("Unable to update price for product: " + productName + " vendor: " + productVendor)
            logging.error(putPrice.status_code)
            logging.error(putPrice.reason)
            logging.error(putPrice.content)

