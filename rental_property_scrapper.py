import csv
from bs4 import BeautifulSoup
import os
import traceback

# Constants
LINKS_LIST_DIR = "input"
OUTPUT_FILE = "output.csv"


def scrapPropertyPage(path):
    f = open(path, "r", encoding="utf8")
    page = f.read()

    output_data = []
    soup = BeautifulSoup(page, 'html.parser')

    # Find link
    link = soup.find(rel="canonical")['href']
    output_data.append(link)

    # Get price
    price = soup.find(itemprop='price')['content']
    output_data.append(price)

    # Get Available Date
    available_date = soup.find("h4", class_="label-block", text="Availability") \
        .find_parent().find_parent().find("td", class_="value-block").text
    output_data.append(available_date)

    # Location
    location_info = soup.find_all('div', attrs={"class": "property-info-element location-info"})
    for item in location_info:
        region = ""
        try:
            region = item.find(itemprop="addressRegion").text
        except AttributeError:
            region = item.find(itemprop="addressLocality").text
        address = item.find(itemprop="streetAddress").text
        postal_code = item.find(itemprop="postalCode").text
        output_data.append(region)
        output_data.append(address)
        output_data.append(postal_code)
        break

    # MRT
    poi_list = soup.find(class_="price-overview-nearby-poi")
    mrt_list = poi_list.find_all('div', attrs={"class": "mrt-line"})
    for item in mrt_list:
        # parse
        mrt_info = item.text
        mrt_info = mrt_info.split(" mins (")
        dist_to_mrt_mins = mrt_info[0]
        mrt_info = mrt_info[1].split(" m) to ")
        dist_to_mrt_meter = mrt_info[0]
        mrt_station = mrt_info[1]

        output_data.append(mrt_station)
        output_data.append(dist_to_mrt_mins)
        output_data.append(dist_to_mrt_meter)
        break

    # Get TOP (year built)
    year_built = soup.find(class_="completion-year").find(class_="value-block").text
    output_data.append(year_built)

    # Get Furnishing
    furnishing_status = soup.find("h4", class_="label-block", text="Furnishing") \
        .find_parent().find_parent().find("td", class_="value-block").text
    output_data.append(furnishing_status)

    # Description
    desc = soup.find(class_="listing-details-text").text.strip()
    output_data.append(processDescription(desc))

    # Agent info
    agent_details_div = soup.find(class_="agent-details-container")
    agent_name = agent_details_div.find(class_="list-group-item-heading").text
    output_data.append(agent_name.strip())

    agent_contact_div = soup.find(class_="agent-phone")
    agent_number = agent_contact_div.find(class_="agent-phone-number").text
    output_data.append(processAgentNumber(agent_number))
    return output_data


def processAgentNumber(agent_number):
    return agent_number.strip().replace("+", "").replace(" ", "")


def processDescription(description_text):
    return description_text.replace("Description\n", "").replace("\n\n", "\n")


def writeOutputToCsv(result):
    with open(OUTPUT_FILE, mode='w', newline='', encoding="utf8") as output_file:
        file_writer = csv.writer(output_file, delimiter=',')
        for data in result:
            file_writer.writerow(data)


output = []
for filename in os.listdir(LINKS_LIST_DIR):
    if filename.endswith(".htm"):
        print(filename)
        path = os.path.join(LINKS_LIST_DIR, filename)
        try:
            output.append(scrapPropertyPage(path))
        except AttributeError:
            traceback.print_exc()

writeOutputToCsv(output)
