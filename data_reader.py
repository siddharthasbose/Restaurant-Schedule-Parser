import os
import tempfile
import unittest
import pandas as pd
import logging
import re

from utils import ParserUtils

logging.basicConfig( level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')

class DataReader:
    def __init__(self, filenames):
        self.filenames = filenames
        self.df = self._parse_files()

    def _parse_files(self):
        """ 
        1. Loop through input files
        2. Open file and read line
        3. Check if comma separated - clean up string if not
        4. Append data in a list 
        5. Create Dataframe with restaurant name and timings string

        Returns:
            dataframe: Name of Restaurants and their timings
        """
        rows = []
        try:
            for filename in self.filenames:
                
                if(ParserUtils.is_valid_csv(filename)):
                    logging.info(f"{filename} validated")
                    with open(filename, 'r') as file:
                        for line in file:
                            line = line.strip()
            
                            parts = line.split(',', 1)
                            if len(parts) == 1:
                            #TODO: Validate multiple splits
                                match = re.search(r"(.*?)((?:mon|tue|wed|thu|fri|sat|sun).*?(?:am|pm).*$)", line, re.IGNORECASE)
                                if match:
                                    start_index = match.start()
                                    rows.append(ParserUtils.clean_string(line[:start_index]), ParserUtils.clean_string(line[start_index:]))
                            else:    
                                rows.append((ParserUtils.clean_string(parts[0]), ParserUtils.clean_string(parts[1])))
                            logging.debug(rows)
                else:
                    raise Exception("Invalid file")
        except FileNotFoundError as f:
            logging.error(f"Error :{f}")
            raise f
        except Exception as e:
            logging.error(f"Error :{e}")

        return pd.DataFrame(rows, columns=['Restaurant', 'Timings'])

    def get_restaurants_df(self):
        return self.df

    def get_timings(self, restaurant_name):
        timing = self.df[self.df['Restaurant'] == restaurant_name]['Timings']
        return timing.values[0] if not timing.empty else None

class TestDataReader(unittest.TestCase):

    def setUp(self):
        # Create temporary directory
        self.temp_dir = tempfile.TemporaryDirectory()
        self.sample1_path = os.path.join(self.temp_dir.name, "sample1.csv")
        self.sample2_path = os.path.join(self.temp_dir.name, "sample2.csv")
        
        # Creating the sample files
        with open(self.sample1_path, "w") as f:
            f.write("Sapporo-Ya Japanese Restaurant, Mon-Sat 11 am - 11 pm  / Sun 11 am - 10:30 pm \" ," )

        with open(self.sample2_path, "w") as f:
            f.write("Santorini's Mediterranean Cuisine , Mon-Sun 8 am - 10:30 pm ,\n")
    
    def test_restaurant_timings(self):
    
        # Parsing the files
        files = [self.sample1_path, self.sample2_path]
        reader = DataReader(files)

        # Fetching the DataFrame
        df = reader.get_restaurants_df()

        # Asserting the values are correct
        self.assertEqual(reader.get_timings("Sapporo-Ya Japanese Restaurant"), "Mon-Sat 11 am - 11 pm  / Sun 11 am - 10:30 pm")
        self.assertEqual(reader.get_timings("Santorini's Mediterranean Cuisine"), "Mon-Sun 8 am - 10:30 pm")

    def tearDown(self):
        # Cleanup temporary directory after the test completes
        self.temp_dir.cleanup()

if __name__ == '__main__':
    unittest.main()
