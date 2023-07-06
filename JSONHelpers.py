import ujson

# JSON Helpers
class JSONHelpers:
    @staticmethod
    def append_to_json_file(new_data, filename='test-data.json'):
        try:
            # Open the file in read mode
            with open(filename, 'r') as file:
                    # Load the existing JSON data
                    file_data = ujson.load(file)
        except OSError:
            # If the file doesn't exist, create an empty dictionary
            file_data = {}

        # Append the new data to the existing data
        file_data.update(new_data)

        # Open the file in write mode
        with open(filename, 'w') as file:
            # Write the updated data back to the file
            ujson.dump(file_data, file)

    @staticmethod
    def remove_from_json_file(key, filename='test-data.json'):
        try:
            # Open the file in read mode
            with open(filename, 'r') as file:
                # Load the existing JSON data
                file_data = ujson.load(file)
        except OSError:
            # If the file doesn't exist, return without making any changes
            return

        # Remove the key from the dictionary
        if key in file_data:
            del file_data[key]

        # Open the file in write mode
        with open(filename, 'w') as file:
            # Write the updated data back to the file
            ujson.dump(file_data, file)
     
    @staticmethod
    def empty_json_file(filename='test-data.json'):
        # Create an empty dictionary
        file_data = {}

        # Open the file in write mode
        with open(filename, 'w') as file:
            # Write the empty data to the file
            ujson.dump(file_data, file)
            
    @staticmethod
    def read_json_file(filename = 'test-data.json'):
        try:
            # Open the file in read mode
            with open(filename, 'r') as file:
                data = ujson.load(file)
            return data
        except OSError:
            # If the file doesn't exist or there is an error reading it return None
            return None
