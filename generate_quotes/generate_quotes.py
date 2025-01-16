import random
import string
from openai import OpenAI
import os
import re


client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Define the structure for each quote
def generate_quote(hour, minute: int, prev_quotes):
    """
    Generates a prompt to create a robot-themed quote for a given minute of the hour.
    Adjusts time format for variety and places it correctly in the sentence.
    """
    # hour = "00"
    # chosen_time = generate_time_string(hour, minute)


    while True:
        try:

            # Define a list of types of literature
            types_of_literature = [
                "mystic poem",
                "Haruki Murakami", "Virginia Woolf", "Gabriel García Márquez", "Ernest Hemingway", "James Joyce", "Toni Morrison", "David Foster Wallace", "Cormac McCarthy", "Margaret Atwood", "Zadie Smith", "Kurt Vonnegut", "Raymond Chandler", "Flannery O'Connor", "Chuck Palahniuk", "Isabel Allende"
            ]

            # Select a random type of literature from the list
            selected_type = random.choice(types_of_literature)
            time_location = random.choice(["start", "middle", "end"])
            loquacity = random.choice(["sparse", "ornate", "brief", "very short"])
            style = random.choice(["abstract", "poetic", "concrete with names, places, etc", "koan-like", "concrete with specific robots", "haiku-like", "profound", "factual"])
            focus = random.choice(["a specific robot", "a person with robot", "a person using AI", "people using AI", "people with robots"])

            # ask chatgpt for a comma separated list of ways to expres the time hour:minute
            response = client.chat.completions.create(

                messages=[
                {
                    "role": "system", "content": "You are a creative assistant.",
                    "role": "user", "content": f"Give me a comma separated list of 3 ways to express the time {hour}:{minute} biased toward the straightfoward in writing in the style of:{selected_type}. There should be no explanations included, and no puctuation other than commas."
                }
                ],
                model="gpt-4o",
                temperature=0.3,  # low creativity
                max_tokens=100,    # Adjust based on batch size and format
                # frequency_penalty=0.8,  # Reduces repetition
                # presence_penalty=0.5     # Encourages exploration of new ideas
            )

            response_text = response.choices[0].message.content
            # print(response_text)

            # Convert the comma-separated list into a Python list
            time_expressions = [time.strip() for time in response_text.split(',')]

            # Select a random time expression from the list
            chosen_time = random.choice(time_expressions)

            """
            Generates a pair of random uppercase initials.
            """
            first_initial = random.choice(string.ascii_uppercase)
            second_initial = random.choice(string.ascii_uppercase)

            print(f"type: {selected_type}")
            print(f"style: {style}")
            print(f"loquacity: {loquacity}")
            print(f"focus: {focus}")
            print(f"chosen time: {chosen_time}")
            print(f"Initials: {first_initial}{second_initial}")


            prompt = (
                "Generate a quote about a humans and robots and AI working together."
                "The quote must be thought provoking and quirky, whimsical, or poetic."
                "Text should not say this directly, however they draw from a projected future where human life and capabilities are enhanced by robots and artificial intelligence."
                f"The quote must focus on {focus} and should be in the style of:{selected_type}, with loquacity: {loquacity} and style: {style}."
                "If this style supports it, the text should be grounded around a single actor, be they a person, robot or AI."
                f"Quote must includes the specific text {chosen_time} somewhere near the {time_location} of the sentence."
                f"Time of day for the quote is {hour:02}:{minute:02}."
                "The quote must be shorter than 600 characters."
                "Generate a fictional title, author, and publication year in the future (between 2040 and 2100)."
                f"Author initials are: {first_initial}{second_initial}."
                "Format should be as follows with a newline between each item."
                "Quote: \"<quote>\" "
                "Title: <title> "
                "Author: <author> "
                "Year: <year>"
            )
            response = client.chat.completions.create(

                messages=[
                {
                    "role": "system", "content": "You are a globally renowned writer, critically acclaimed for your wit, insight and wisdom.",
                    "role": "user", "content": prompt
                }
                ],
                model="gpt-4o",
                temperature=0.6,  # High creativity
                max_tokens=200,    # Adjust based on batch size and format
                frequency_penalty=0.8,  # Reduces repetition
                presence_penalty=0.4     # Encourages exploration of new ideas
            )

            response_text = response.choices[0].message.content
            print(response_text+"\n")
            
            # Validate and parse the response
            parsed_data = validate_response(response_text)
            break

        except ValueError as e:
            print(f"Validation error: {e}. Retrying ...")

    # confirm that chosen_time is correct for cases used in quote
    quote = parsed_data['Quote']
    time_match = re.search(re.escape(chosen_time), quote, re.IGNORECASE)
    if time_match:
        # Update chosen_time to match the form used in the quote
        chosen_time = time_match.group(0)
    else:
        raise ValueError(f"Chosen time '{chosen_time}' not found in the quote")

    # parsed_data['chosen_time'] = chosen_time
    parsed_data['time_string'] = chosen_time
    parsed_data['hour'] = hour
    parsed_data['minute'] = minute

    print(parsed_data["Quote"])
    print("------------------\n")

    return parsed_data


def format_entry(parsed_data: dict) -> str:
    """
    Formats the quote entry into the required format.
    """
    digital_time = f"{parsed_data['hour']:02d}:{parsed_data['minute']:02d}"
    return f"{digital_time}|{parsed_data['time_string']}|{parsed_data['Quote']}|{parsed_data['Title']} ({parsed_data['Year']})|{parsed_data['Author']}"



# Validate API response to match the specified format
def validate_response(response_text: str) -> dict:
    """
    Parses and validates the response from the API. Checks if the expected fields (Quote, Title, Author, Year)
    are present and formatted correctly. Allows for extra whitespace or newlines but excludes them in the captured data.
    """

    patterns = {
        'Quote': r'Quote:\s*(.*?)\s*(?=Title:)',  # Capture until "Title:" on a new line
        'Title': r'^Title:\s*(.*)\s*(?=Author:)',
        'Author': r'^Author:\s*(.*)\s*(?=Year:)',
        'Year': r'^Year:\s*(\d{4})'
    }
    parsed_data = {}
    
    for field, pattern in patterns.items():
        match = re.search(pattern, response_text, re.MULTILINE | re.DOTALL)  # Enable dot to match newlines
        if not match:
            raise ValueError(f"Missing or misformatted field: {field}")
            
        # Strip spurious newlines or extra spaces
        parsed_data[field] = match.group(1).replace('\n', ' ').strip()
    
    # Validate that the quote is no longer than 600 characters
    quote = parsed_data['Quote']
    if len(quote) > 600:
        raise ValueError("Quote exceeds 600 characters")
    
    # print (parsed_data)
    return parsed_data


# Main function to generate and save quotes for an entire hour range
def generate_hour_quotes(hour="00"):
    """
    Generates quotes for each minute in the specified hour.
    """
    entries = []
    prev_quotes = []
    for minute in range(60):
        try:
            parsed_data = generate_quote(hour, minute, prev_quotes)
            formatted_entry = format_entry(parsed_data)
            entries.append(formatted_entry)

            prev_quotes.append(parsed_data["Quote"])
        except ValueError as e:
            print(f"Error at {hour}:{minute:02d} - {e}")

    # Save to a file
    with open(f"robot_quotes_{hour:02d}.txt", "w") as f:
        f.write("\n".join(entries))
    print(f"Generated quotes for hour {hour:02d} saved to robot_quotes_{hour:02d}.txt")


# Generate quotes for each hour from 9am to 7pm
for hour in range(0,24):
    generate_hour_quotes(hour)
