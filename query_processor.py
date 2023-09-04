import logging
import os
import pandas as pd
import re
from datetime import datetime, time
from typing import List, Dict, Optional, Union
import unittest

filename = os.path.basename(__file__)

logging.basicConfig( level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(filename)

class QueryProcessor:

    def get_open_restaurants(df: pd.DataFrame, day: str, input_time: Optional[str] = None) -> list:
        """
        Finds list of open restaurants during a given day of the week and time
        Args:
            df (pd.DataFrame): Processed dataframe with restaurant schedule
            day (str): Day of the week in %a format: Mon / Tue / Wed etc 
            input_time (Optional[str], optional): 12 hour time format. Defaults to None.

        Returns:
            list: Returns the list of open restaurants for a given day and time
        """
        try:
            mask = (df['day'] == day)
            if input_time:
                input_datetime = datetime.strptime(input_time, "%I:%M %p") if ":" in input_time else datetime.strptime(input_time, "%I %p")
                mask &= (df['open_time'] <= input_datetime) & (df['close_time'] >= input_datetime)

            open_restaurants = df[mask]['restaurant_name'].unique().tolist()
        except Exception as e:
            logger.error(e)
            raise e
        return open_restaurants


    def get_restaurant_open_timings(df: pd.DataFrame, restaurant_names: Union[str, list]) -> dict:
        """
        Finds open timing for a list of restaurants

        Args:
            df (pd.DataFrame): Processed dataframe with restaurant schedule
            restaurant_names (Union[str, list]): A List of restaurants 

        Returns:
            dict: Name of restaurant and a list of open-close timings
        """
        try:

            if isinstance(restaurant_names, str):
                restaurant_names = [restaurant_names]

            relevant_data = df[df['restaurant_name'].isin(restaurant_names)]


            timings_dict = {}
            for restaurant in restaurant_names:
                restaurant_df = relevant_data[relevant_data['restaurant_name'] == restaurant]
                timings_list = []
                for _, row in restaurant_df.iterrows():
                    timings_list.append(f"{row['day']}: {row['open_time'].strftime('%I:%M %p')} - {row['close_time'].strftime('%I:%M %p')}")
                timings_dict[restaurant] = timings_list
        except Exception as e:
            logger.error(e)
            raise e
        
        return timings_dict

    def generate_insights(df):
        """
        General Insights and aggregates

        Args:
            df (pd.Dataframe): Processed dataframe with restaurant schedule

        Returns:
            dict: Dictionary of insights
        """        """"""
        try:
            insights = {}

            # General Insights
            insights['total_restaurants'] = df['restaurant_name'].nunique()
            common_open_time = df['open_time'].mode()[0]
            common_close_time = df['close_time'].mode()[0]
            insights['most_common_open_time'] = common_open_time
            insights['most_common_close_time'] = common_close_time

            df['duration'] = (df['close_time'] - df['open_time']).dt.total_seconds() / 3600
            insights['average_duration'] = df['duration'].mean()

            # Peak Hours
            hours = [i for i in range(24)]
            open_counts = [0 for _ in range(24)]

            for _, row in df.iterrows():
                for hour in range(int(row['open_time'].hour), int(row['close_time'].hour)):
                    open_counts[hour] += 1

            peak_hour = hours[open_counts.index(max(open_counts))]
            insights['most_busy_hour'] = peak_hour

            # Day specific insights
            weekend_restaurants = df[df['day'].isin(['Sat', 'Sun'])]['restaurant_name'].nunique()
            insights['weekend_restaurants'] = weekend_restaurants
            
            sat_restaurants = df[df['day'].isin(['Sat'])]['restaurant_name'].nunique()
            insights['sat_restaurants'] = sat_restaurants
            
            sun_restaurants = df[df['day'].isin(['Sun'])]['restaurant_name'].nunique()
            insights['sun_restaurants'] = sun_restaurants

            # Operational consistency
            consistent_restaurants = df.groupby('restaurant_name').nunique()['open_time']
            insights['consistent_operating_restaurants'] = consistent_restaurants[consistent_restaurants == 1].count()
        except Exception as e:
            logger.error(e)
            raise e
        return insights
    
class TestQueryProcessor(unittest.TestCase):

    def setUp(self):
        '''
        A-1 Cafe Restaurant	Mon 11 am - 10 pm
        Nick's Lighthouse	Mon-Tue 11 am - 1:00 am
        '''

        self.sample_data = {
            'restaurant_name': ['A-1 Cafe Restaurant', 'Nick\'s Lighthouse', 'Nick\'s Lighthouse', 'Nick\'s Lighthouse', 'Nick\'s Lighthouse'],
            'day': ['Mon', 'Mon', 'Tue', 'Tue', 'Wed'],
            'open_time': [datetime.strptime("11:00 AM", "%I:%M %p"), datetime.strptime("11:00 AM", "%I:%M %p"), datetime.strptime("12:00 AM", "%I:%M %p"), datetime.strptime("11:00 AM", "%I:%M %p"), datetime.strptime("12:00 AM", "%I:%M %p")],
            'close_time': [datetime.strptime("10:00 PM", "%I:%M %p"), datetime.strptime("11:59 PM", "%I:%M %p"), datetime.strptime("01:00 AM", "%I:%M %p"), datetime.strptime("11:59 PM", "%I:%M %p"), datetime.strptime("01:00 AM", "%I:%M %p")]
        }
        self.df = pd.DataFrame(self.sample_data)

    def test_get_open_restaurants(self):
        # Test for Monday 11:30 AM
        result = QueryProcessor.get_open_restaurants(self.df, 'Mon', '11:30 AM')
        self.assertEqual(set(result), set(['A-1 Cafe Restaurant', 'Nick\'s Lighthouse']))

        # Test for Monday 10:45 PM
        result = QueryProcessor.get_open_restaurants(self.df, 'Mon', '10:45 PM')
        self.assertEqual(result, ['Nick\'s Lighthouse'])

    def test_get_restaurant_open_timings(self):
        # Test for single restaurant
        result = QueryProcessor.get_restaurant_open_timings(self.df, 'Nick\'s Lighthouse')
        expected_result = {
            'Nick\'s Lighthouse': ['Mon: 11:00 AM - 11:59 PM', 'Tue: 12:00 AM - 01:00 AM', 'Tue: 11:00 AM - 11:59 PM', 'Wed: 12:00 AM - 01:00 AM']
        }
        self.assertEqual(result, expected_result)

        # Test for multiple restaurants
        result = QueryProcessor.get_restaurant_open_timings(self.df, ['A-1 Cafe Restaurant', 'Nick\'s Lighthouse'])
        expected_result = {
            'A-1 Cafe Restaurant': ['Mon: 11:00 AM - 10:00 PM'],
            'Nick\'s Lighthouse': ['Mon: 11:00 AM - 11:59 PM', 'Tue: 12:00 AM - 01:00 AM', 'Tue: 11:00 AM - 11:59 PM', 'Wed: 12:00 AM - 01:00 AM']
        }
        self.assertEqual(result, expected_result)

if __name__ == '__main__':
    unittest.main()
