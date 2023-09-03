from data_processor import DataProcesser
from data_reader import DataReader
from query_processor import QueryProcessor
import logging

logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')

def main():
    # 1. Read the data
    filenames = ["input_files\dining_places_open_hrs_1.csv", "input_files\dining_places_open_hrs_2.csv"]
    logging.info("Reading files {}".format(filenames))
    reader = DataReader(filenames)

    # Fetching the DataFrame
    logging.info("Processing data into Data Frame")
    df = reader.get_restaurants_df()

    # 2. Process the data
    logging.info("Parsing the resturant schedules")
    processed_data = DataProcesser.build_restaurant_df(df)

    # 3. Query
    day = 'Mon'
    time = '11:30 am'
    logging.info(f"Restaurans open during {day} {time}")
    logging.info(QueryProcessor.get_open_restaurants(processed_data, 'Mon', '11:30 AM'))

    day = 'Sat'
    logging.info(f"Restaurans open during {day}")
    logging.info(QueryProcessor.get_open_restaurants(processed_data, 'Sat'))

    # Query restaurant timings
    rest = ['A-1 Cafe Restaurant', 'Nick\'s Lighthouse']
    logging.info("Restaurant Schedule")
    logging.info(QueryProcessor.get_restaurant_open_timings(processed_data, rest))


if __name__ == "__main__":
    main()