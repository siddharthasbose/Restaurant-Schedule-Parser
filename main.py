import os
import traceback
from data_processor import DataProcesser
from data_reader import DataReader
from query_processor import QueryProcessor
import logging

filename = os.path.basename(__file__)

logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(filename)

def main():
    try:
        # 1. Read the data
        filenames = ["input_files\dining_places_open_hrs_1.csv", "input_files\dining_places_open_hrs_2.csv"]
        logger.info("Reading files {}".format(filenames))
        reader = DataReader(filenames)

        # Fetching the DataFrame
        logger.info("Processing data into Data Frame")
        df = reader.get_restaurants_df()

        # 2. Process the data
        logger.info("Parsing the resturant schedules")
        processed_data = DataProcesser.build_restaurant_df(df)

        # 3. Query
        day = 'Mon'
        time = '11:30 am'
        logger.info(f"Restaurans open during {day} {time}")
        logger.info(QueryProcessor.get_open_restaurants(df=processed_data, day = 'Mon', input_time = '11:30 AM'))

        day = 'Sat'
        logger.info(f"Restaurans open during {day}")
        logger.info(QueryProcessor.get_open_restaurants(df = processed_data, day = 'Sat'))

        # Query restaurant timings
        rest = ['A-1 Cafe Restaurant', 'Nick\'s Lighthouse']
        logger.info("Restaurant Schedule")
        logger.info(QueryProcessor.get_restaurant_open_timings(df = processed_data, restaurant_names=rest))

        #insights
        logger.info("Restaurant Schedule Insights")
        logger.info(QueryProcessor.generate_insights(processed_data))
    except Exception as e:
        logger.error(e)

if __name__ == "__main__":
    main()