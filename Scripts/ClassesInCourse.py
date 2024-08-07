import requests
from bs4 import BeautifulSoup
from pathlib import Path

def get_classes_for_course(course_acronym):
    # URL format for a specific course
    url = f"https://open.fing.edu.uy/courses/{course_acronym}/"
    
    # Send a GET request to the URL
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content using BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the div with class="class-list"
        class_list_div = soup.find('div', class_='class-list')
        
        # List to store class numbers
        class_numbers = []
        
        # Check if the class-list div exists
        if class_list_div:
            # Find all 'a' tags with class="class-list__item" inside the class-list div
            classes = class_list_div.find_all('a', class_='class-list__item')
            
            for class_item in classes:
                # Extract the class number from the href attribute
                href = class_item.get('href')
                if href:
                    class_number = href.split('/')[-2]  # Get the part after "https://open.fing.edu.uy/courses/{courseAcronym}/"
                    class_numbers.append(class_number)
        
        return class_numbers
    else:
        print(f"Failed to retrieve the page for {course_acronym}. Status code: {response.status_code}")
        return []

def main():
    # Path to the file containing course acronyms
    course_acronyms_path = Path("../DB/CoursesNames/course_acronyms.txt")
    
    # Check if the course acronyms file exists
    if not course_acronyms_path.exists():
        print(f"File not found: {course_acronyms_path}")
        return
    
    # Read course acronyms from the file
    with open(course_acronyms_path, 'r') as file:
        course_acronyms = [line.strip() for line in file if line.strip()]
    
    # Process each course acronym
    for acronym in course_acronyms:
        classes = get_classes_for_course(acronym)
        
        # Define the output path for classes.txt
        output_dir = Path(f"../DB/Opens/{acronym}/")
        output_dir.mkdir(parents=True, exist_ok=True)  # Create directories if they don't exist
        output_file = output_dir / "classes.txt"
        
        # Write class numbers for each acronym to a file
        with open(output_file, 'w') as class_file:
            for class_number in classes:
                class_file.write(f"{class_number}\n")
        
        print(f"Class numbers for course {acronym} have been written to {output_file}")

if __name__ == "__main__":
    main()
