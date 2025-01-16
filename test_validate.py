import re

def validate_response(response_text: str) -> dict:
    """
    Parses and validates the response from the API. Checks if the expected fields (Quote, Title, Author, Year)
    are present and formatted correctly. Allows for extra whitespace or newlines but excludes them in the captured data.
    """
    # Regular expression patterns for each required field with flexible whitespace handling
    patterns = {
        'Quote': r'Quote:\s*(.*?)\s*(?=^Title:)',  # Capture until "Title:" on a new line
        'Title': r'^Title:\s*(.*)$',
        'Author': r'^Author:\s*(.*)$',
        'Year': r'^Year:\s*(\d{4})$'
    }
    parsed_data = {}
    
    for field, pattern in patterns.items():
        match = re.search(pattern, response_text, re.MULTILINE | re.DOTALL)  # Enable dot to match newlines and multiline mode
        if not match:
            raise ValueError(f"Missing or misformatted field: {field}")
        # Strip spurious newlines or extra spaces
        parsed_data[field] = match.group(1).replace('\n', ' ').strip()
    
    # print(parsed_data)
    return parsed_data

# Example usage
response_text = """
Quote: "This is a multi-line quote
that spans several lines."

Title: Example Title
Author: Example Author
Year: 2045
"""

parsed_data = validate_response(response_text)
print(parsed_data)