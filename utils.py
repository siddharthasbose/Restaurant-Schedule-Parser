import logging
import os
from pathlib import Path
import pandas as pd
import re
from datetime import datetime, time
from typing import List, Dict, Optional, Union
import unittest

logging.basicConfig( level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

class ParserUtils:

    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

    @staticmethod
    def extract_days(weekday_str: str) -> List[str]:
        """
        Extract a list of week days for a given range

        Args:
            weekday_str (str): Days the resturant is open
            Example: "Mon, Fri", "Mon-Wed, Sun", "Fri-Tue, Sun"

        Returns:
            List[str]: List of weekdays that fall in the input range 
        """        
        extracted_days = []

        # Split on comma first to handle formats like "Mon-Thu, Sun"
        for segment in weekday_str.split(","):
            segment = segment.strip()

            # If it's a range separated by -
            if '-' in segment:
                start_day, end_day = segment.split('-')
                start_index = ParserUtils.days.index(start_day)
                end_index = ParserUtils.days.index(end_day)

                # Check range definition Thu - Mon (3 -> 0) / Sat - Mon (5 -> 0) instead of Mon - Fri (0 -> 4)
                if start_index > end_index:
                    for i in range(start_index, len(ParserUtils.days)):
                        extracted_days.append(ParserUtils.days[i])
                    for i in range(0, end_index + 1):
                        extracted_days.append(ParserUtils.days[i])
                else:
                    for i in range(start_index, end_index + 1):
                        extracted_days.append(ParserUtils.days[i])
            else:
                extracted_days.append(segment)

        return extracted_days

    @staticmethod
    def extract_time(time_str: str) -> (datetime, datetime):
        """
        Extract open and close timings for a given input time string

        Args:
            time_str (str): Timing string (11:00 am - 11 pm)

        Returns:
            datetime: Open time
            datetime: Closing time

        """
        # Extract timings using regex
        times = re.findall(r'(\d{1,2}(?::\d{2})?\s*[apm]{2})', time_str, re.IGNORECASE)

        try:
            open_time = datetime.strptime(times[0], "%I:%M %p") if ":" in times[0] else datetime.strptime(times[0], "%I %p")
            close_time = datetime.strptime(times[1], "%I:%M %p") if ":" in times[1] else datetime.strptime(times[1], "%I %p")
        except ValueError as ve:
            logging.error("Failed to parse time %s %s", time_str, ve)
        return open_time, close_time
    
    @staticmethod
    def clean_string(input_str: str) -> (str):
        return input_str.strip(' ",')
    
    @staticmethod
    def is_valid_csv(file_path: str) -> bool:
        # Check if file exists
        if not os.path.exists(file_path):
            logging.error(f"{file_path} does not exist.")
            return False
        
        # Check file size (example: > 0 bytes)
        if os.path.getsize(file_path) == 0:
        # if Path(file_path).stat().st_size == 0:
            logging.error(f"{file_path} is empty.")
            return False

        return True
    
class TestParserUtils(unittest.TestCase):

    def test_extract_days(self):
        # Test basic day extraction
        self.assertEqual(ParserUtils.extract_days('Mon'), ['Mon'])
        
        # Test range extraction
        self.assertEqual(ParserUtils.extract_days('Mon-Fri'), ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'])
        
        # Test range extraction for non serial range
        self.assertEqual(ParserUtils.extract_days('Fri-Sun'), ['Fri', 'Sat', 'Sun'])
        self.assertEqual(ParserUtils.extract_days('Sat-Mon'), ['Sat', 'Sun', 'Mon'])

        # Test combined format
        self.assertEqual(ParserUtils.extract_days('Mon-Wed, Fri'), ['Mon', 'Tue', 'Wed', 'Fri'])
        self.assertEqual(ParserUtils.extract_days('Mon, Thu-Sun'), ['Mon', 'Thu', 'Fri', 'Sat', 'Sun'])

    def test_extract_time(self):
        # Test basic timings
        self.assertEqual(ParserUtils.extract_time('11 am - 1 pm'), (datetime.strptime('11:00 AM', "%I:%M %p"), datetime.strptime('1:00 PM', "%I:%M %p")))
        
        # Test timings without minutes
        self.assertEqual(ParserUtils.extract_time('11 am - 1 pm'), (datetime.strptime('11:00 AM', "%I:%M %p"), datetime.strptime('1:00 PM', "%I:%M %p")))
        self.assertEqual(ParserUtils.extract_time('2 pm - 4 pm'), (datetime.strptime('2:00 PM', "%I:%M %p"), datetime.strptime('4:00 PM', "%I:%M %p")))
        
        # Test timings with minutes
        self.assertEqual(ParserUtils.extract_time('11:30 am - 1:45 pm'), (datetime.strptime('11:30 AM', "%I:%M %p"), datetime.strptime('1:45 PM', "%I:%M %p")))
        
        # Test mixed minutes
        self.assertEqual(ParserUtils.extract_time('9 pm -11:59 am'), (datetime.strptime('9:00 PM', "%I:%M %p"), datetime.strptime('11:59 AM', "%I:%M %p")))

    def test_clean_string(self):
        # Test basic timings
        self.assertEqual(ParserUtils.clean_string('"Mon -Fri 11 am - 1 pm,'), "Mon -Fri 11 am - 1 pm")
        self.assertEqual(ParserUtils.clean_string('Mon -Fri 11 am - 1 pm",'), "Mon -Fri 11 am - 1 pm")

    def test_is_valid_csv(self):
        self.assertFalse(ParserUtils.is_valid_csv("input_files\empty_file.csv"))
        self.assertFalse(ParserUtils.is_valid_csv("input_files\invalid_file.csv"))
        self.assertTrue(ParserUtils.is_valid_csv("input_files\dining_places_open_hrs_1.csv"))
        self.assertTrue(ParserUtils.is_valid_csv("input_files\empty.csv"))

if __name__ == '__main__':
    unittest.main()
