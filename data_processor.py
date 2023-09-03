import logging
import pandas as pd
import re
from datetime import datetime, time
from typing import List, Dict, Optional, Union
import unittest
from utils import ParserUtils

logging.basicConfig( level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

class DataProcesser:

    def build_restaurant_df(df: pd.DataFrame) -> pd.DataFrame:
        """
        1. Read the dataframe with restaurant names and timings
        2. Iterate through timings separated by /
        3. Split the timing string to day of the week and the time range
        4. Iterate over the days of the week and and store timings for each day
        5. Handle 24 hour boundary to capture open timings after 12:00 AM
        6. Returns a dataframe with multiple rows (if restaurant is open for multiple time windows) 
           for restaurant names, day of week, open and close timings

        Args:
            df (pd.DataFrame): DataFrame with restaurant name and timings  

        Returns:
            pd.DataFrame: DataFrame with restaurants, day of week, open and close timings 
        """            
        records = []

        for index, row in df.iterrows():
            restaurant, timings = row['Restaurant'], row['Timings']
            logging.debug(f"Building {restaurant} {timings}")
            restaurant = restaurant.strip()
            for timing in timings.split('/'):
                weektimings = re.match(r"(.*?)\s+(?=\d+)(.*)", timing.strip()) # TODO Consider moving to constants?
                days_str = weektimings.group(1)
                times_str = weektimings.group(2)

                start_time, end_time = ParserUtils.extract_time(times_str)

                # If end_time < start_time, means the time is beyond 24 hours and flows to the next day
                if end_time and start_time and end_time < start_time:
                    for day in ParserUtils.extract_days(days_str):
                        records.append((restaurant, day, start_time, datetime.strptime("11:59 PM", "%I:%M %p")))
                        next_day = ParserUtils.days[(ParserUtils.days.index(day) + 1) % 7]
                        records.append((restaurant, next_day, datetime.strptime("12:00 AM", "%I:%M %p"), end_time))
                else:
                    for day in ParserUtils.extract_days(days_str):
                        records.append((restaurant, day, start_time, end_time))

        df = pd.DataFrame(records, columns=['restaurant_name', 'day', 'open_time', 'close_time'])
        logging.debug(df)
        return df

class TestQueryProcessor(unittest.TestCase):

    def setUp(self):

        self.sample_data = {
            'Restaurant': [
                "A-1 Cafe Restaurant", "Nick's Lighthouse", "Paragon Restaurant & Bar", "Chili Lemon Garlic",
                "Bow Hon Restaurant", "San Dong House", "Thai Stick Restaurant", "Jayce's night club"
            ],
            'Timings': [
                "Mon, Wed-Sun 11 am - 10 pm", "Mon-Sun 11 am - 10:30 pm",
                "Mon-Fri 11:30 am - 10 pm  / Sat 5:30 pm - 10 pm", "Mon-Fri 11 am - 10 pm  / Sat-Sun 5 pm - 10 pm",
                "Mon-Sun 11 am - 10:30 pm", "Mon-Sun 11 am - 11 pm", "Mon-Sun 11 am - 1 am", "Mon 7 am - 12 am / Tue 7 am - 12 am / Sun 9 AM - 9 PM"
            ]
        }
    
    def test_build_restaurant_df(self):   
        df = pd.DataFrame(self.sample_data)
        result_df = DataProcesser.build_restaurant_df(df)
        logging.debug(result_df)
        # Test cases for "A-1 Cafe Restaurant"
        self.assertEqual(len(result_df[result_df['restaurant_name'] == "A-1 Cafe Restaurant"]), 6)
        monday_open_time = result_df[
            (result_df['restaurant_name'] == "A-1 Cafe Restaurant") & 
            (result_df['day'] == 'Mon')]['open_time'].iloc[0]
        self.assertEqual(monday_open_time, datetime.strptime("11:00 AM", "%I:%M %p"))

        # Test cases for "Thai Stick Restaurant" which crosses midnight
        self.assertEqual(len(result_df[result_df['restaurant_name'] == "Thai Stick Restaurant"]), 14)
        wednesday_open_time = result_df[
            (result_df['restaurant_name'] == "Thai Stick Restaurant") & 
            (result_df['day'] == 'Wed')]['open_time'].iloc[1] # opens first at midnight
        self.assertEqual(wednesday_open_time, datetime.strptime("11:00 AM", "%I:%M %p"))

        monday_open_time = result_df[
            (result_df['restaurant_name'] == "Thai Stick Restaurant") & 
            (result_df['day'] == 'Mon')]['open_time'].iloc[1]
        self.assertEqual(monday_open_time, datetime.strptime("12:00 AM", "%I:%M %p"))

        wednesday_close_time = result_df[
            (result_df['restaurant_name'] == "Thai Stick Restaurant") & 
            (result_df['day'] == 'Wed')]['close_time'].iloc[1]
        self.assertEqual(wednesday_close_time, datetime.strptime("11:59 PM", "%I:%M %p"))

        # Test cases for "Jayce's night club" which is open till Monday and Tuesday midnight
        self.assertEqual(len(result_df[result_df['restaurant_name'] == "Jayce's night club"]), 5)
        monday_close_time = result_df[
            (result_df['restaurant_name'] == "Jayce's night club") & 
            (result_df['day'] == 'Mon')]['close_time'].iloc[0] 
        self.assertEqual(monday_close_time, datetime.strptime("11:59 PM", "%I:%M %p"))

        tuesday_open_time = result_df[
            (result_df['restaurant_name'] == "Jayce's night club") & 
            (result_df['day'] == 'Tue')]['open_time'].iloc[0] 
        self.assertEqual(tuesday_open_time, datetime.strptime("12:00 AM", "%I:%M %p"))


if __name__ == '__main__':
    unittest.main()