# This class will contain the modules necessary to extract and present data from the CCP Eve API (ESI)to pull market
# data in relation to planetary interactions (P1 and P4), and only to specifically related items in accordance to
# the python dictionaries

from urllib import request
import os
import time


class Aggregator:
    # Replace the path with where you want the text file dumped. This will not work on root (c:/) and forward slashes,
    # not back slashes must be used. This convention lets the normpath function ensure we have a well-formed path.
    DAILY_ISK_TOTAL = 0.00
    MONTHLY_ISK_TOTAL = 0.00
    PI_STATS_OUT = os.path.normpath("C:/Users/antho/Desktop/eve_market_data.txt")
    GLOBAL_PI_ACTIVE_PULL = "https://esi.tech.ccp.is/latest/markets/prices/?datasource=tranquility"
    HISTORIC_PI_PULL_REGIONAL = "https://esi.tech.ccp.is/latest/markets/10000002/history/?datasource=tranquility&type_id={0}"
    # You can add and remove items that you want to account for in the data sheet by adding an entry, the same as seen
    # below in the appropriate dictionaries
    # Planetary Interaction P1 dictionary:
    PI_P1 = {"Bacteria": "2393",
             "Biofuels": "2396",
             "Biomass": "3779",
             "Chiral Structures": "2401",
             "Electrolytes": "2390",
             "Industrial Fibers": "2397",
             "Oxidizing Compound": "2392",
             "Oxygen": "3683",
             "Plasmoids": "2389",
             "Precious Metals": "2399",
             "Proteins": "2395",
             "Reactive Metals": "2398",
             "Silicon": "9828",
             "Toxic Metals": "2400",
             "Water": "3645",
             }
    # Planetary Interaction P4 dictionary:
    PI_P4 = {"Broadcast Node": "2867",
             "Integrity Response Drones": "2868",
             "Wetware Mainframe": "2876",
             }
    ITEM_QUANTITY = {"Broadcast Node": 24,
                     "Integrity Response Drones": 24,
                     "Wetware Mainframe": 24,
                     "Bacteria": 15360,
                     "Biofuels": 15360,
                     "Biomass": 11520,
                     "Chiral Structures": 15360,
                     "Electrolytes": 7680,
                     "Industrial Fibers": 11520,
                     "Oxidizing Compound": 11520,
                     "Oxygen": 15360,
                     "Plasmoids": 11520,
                     "Precious Metals": 15360,
                     "Proteins": 7680,
                     "Reactive Metals": 15360,
                     "Silicon": 11520,
                     "Toxic Metals": 7680,
                     "Water": 15360,
                     }

    def getGlobalData(self, statsdict):
        #Clean up the old data file
        try:
            if os.path.isfile(self.PI_STATS_OUT) and statsdict == self.PI_P4:
                os.remove(self.PI_STATS_OUT)
                with open(self.PI_STATS_OUT, 'a') as stats_out:
                    stats_out.write("=========================================================================================\n")
                    stats_out.write("=============Global Data for Planetary Interraction P4 and P1 specific items=============\n")
                    stats_out.write("=========================================================================================\n")
                    stats_out.write("\n******************************\n")
                    stats_out.write("*KEY:*************************\n")
                    stats_out.write("*PPU: Price Per Unit**********\n")
                    stats_out.write("*Daily: Daily ISK instake*****\n")
                    stats_out.write("*Monthly: Monthly ISK instake*\n")
                    stats_out.write("******************************\n\n")
        except IOError as e:
            print(e)
            exit(1)
        with open(self.PI_STATS_OUT, 'a') as stats_out:
            try:
                response = request.urlopen(self.GLOBAL_PI_ACTIVE_PULL)
                for html in response:
                    output = html.decode()
                    item_list = output.split("}")
                    # Extract the type_id to ensure we only work on exact matches
                    for item in item_list:
                        # Trim some erroneous fat from the front of the item strings
                        item = item[2:]
                        item_list = item.split(",")
                        # Fun with built-in python string formatting to get just the value of the type_id
                        type_id = item_list[0][10:]
                        # Dictionary value comparison to the current iteration of type_id. If a match is found, we know
                        # that it's an item of interest and we store that data in the data sheet
                        for k, v in statsdict.items():
                            if v == type_id:
                                price = item_list[1]
                                isk = price.split(":")[1]
                                #Check item quantity in our item quantity dictionary class attribute:
                                item_quantity = self.ITEM_QUANTITY.get(k)
                                item_output = Aggregator().PICalculator(k, isk, item_quantity)
                                stats_out.write("{0}\n".format(item_output))
                                daily_isk = float(item_output.split("|")[2][8:])
                                monthly_isk = float(item_output.split("|")[3][10:])
                                #Check to see if this is a P1 or a P4 item and calculate against total ISK accordingly
                                if statsdict == self.PI_P4:
                                    self.DAILY_ISK_TOTAL += daily_isk
                                    self.MONTHLY_ISK_TOTAL += monthly_isk
                                else:
                                    self.DAILY_ISK_TOTAL -= daily_isk
                                    self.MONTHLY_ISK_TOTAL -= monthly_isk
            except Exception as e:
                print(e)
                exit(1)
                stats_out.write(e)


    def PICalculator(self, item_name, isk_value, desired_quantity):
        isk_value = float(isk_value)
        daily_total = round(isk_value * desired_quantity, 2)
        monthly_total = daily_total * 30
        return "{0} x {1} | PPU: {2} | Daily: {3} | Monthly: {4}".format(item_name, desired_quantity, isk_value,
                                                                         round(daily_total, 2), round(monthly_total, 2))

    #This function will be used to generate ISK totals based on calculation done to the associated class attributes
    def generateISKTotals(self):
        try:
            with open(self.PI_STATS_OUT, 'a') as stats_out:
                stats_out.write("\n\nDaily ISK gain after P1 purchase calculations: {0}\n".format(round(self.DAILY_ISK_TOTAL, 2)))
                stats_out.write("Monthly ISK gain after P1 purchase calculations: {0}\n\n".format(round(self.MONTHLY_ISK_TOTAL, 2)))
        except IOError as e:
            print(e)
            exit(1)

    def getHistoricalRegionData(self, statsdict):
        try:
            with open(self.PI_STATS_OUT, 'a') as stats_out:
                if statsdict == self.PI_P4:
                    stats_out.write("\n\n\n=========================================================================================\n")
                    stats_out.write("==================Historical Data Dump for the Jita region ('The Forge')=================\n")
                    stats_out.write("=========================================================================================\n\n")
                # These url requests return:s data at the byte-level. We need to convert that to a string to do some work to it
                # REMINDER: 'k' is the item name and 'v' is the item ID. We use the Name later for readable output
                for k, v in statsdict.items():
                    stats_out.write(
                            "=========================================================================================\n")
                    stats_out.write(
                            "{0}: Last 90 days of market data for the Jita region of space (The Forge):\n".format(k))
                    stats_out.write(
                            "=========================================================================================\n")
                    # Generate a HTML response and store it in an object
                    response = request.urlopen(self.HISTORIC_PI_PULL_REGIONAL.format(v))
                    for html in response:
                        # Extract the byte data from the html class object from above and convert it into a string
                        # for further processing into relevant data
                        output = html.decode('UTF-8')
                        date_list = output.split("}")
                        # Get the last 90 days
                        date_list = date_list[-90:]
                        for date in reversed(date_list):
                            # Format each line to be standardized to make working with the text data easier
                            date = date[2:]
                            date_data = date.split(',')
                            # Make sure we don't add any erroneous lines
                            if len(date_data) == 6:
                                stats_out.write("{0}\n".format(date_data))
                    stats_out.write("\n\n")
        except Exception as e:
            print(e)

agr = Aggregator()
agr.getGlobalData(Aggregator.PI_P4)
print("Sleeping 5 seconds to avoid requesting too much data simultaneously and causing frequent timeouts")
time.sleep(5)
agr.getGlobalData(Aggregator.PI_P1)
print("Sleeping 5 seconds to avoid requesting too much data simultaneously and causing frequent timeouts")
time.sleep(5)
agr.generateISKTotals()
agr.getHistoricalRegionData(Aggregator.PI_P4)
print("Sleeping 5 seconds to avoid requesting too much data simultaneously and causing timeouts frequently")
time.sleep(5)
agr.getHistoricalRegionData(Aggregator.PI_P1)
