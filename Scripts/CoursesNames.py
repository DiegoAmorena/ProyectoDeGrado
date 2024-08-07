import requests
from bs4 import BeautifulSoup

# URL of the page containing the course list
url = "https://open.fing.edu.uy/courses/"
dbPath = "../DB/CoursesNames/"
# Send a GET request to the URL
response = requests.get(url)

# Check if the request was successful
if response.status_code == 200:
    # Parse the HTML content using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the div with class="course-list"
    course_list_div = soup.find('div', class_='course-list')
    
    # Lists to store acronyms and names
    course_acronyms = []
    course_names = []
    
    # Check if the course-list div exists
    if course_list_div:
        # Find all 'a' tags with class="name course" inside the course-list div
        courses = course_list_div.find_all('a', class_='name course')
        
        for course in courses:
            # Extract the course acronym from the href attribute
            href = course.get('href')
            if href:
                acronym = href.split('/')[-2]  # Get the part after "https://open.fing.edu.uy/courses/"
                course_acronyms.append(acronym)
            
            # Extract the course name from the span with class="course-title"
            course_title_span = course.find('span', class_='course-title')
            if course_title_span:
                course_names.append(course_title_span.text.strip())
    
    # Write acronyms to a file
    with open(dbPath + 'course_acronyms.txt', 'w') as acronym_file:
        for acronym in course_acronyms:
            acronym_file.write(f"{acronym}\n")
    
    # Write names to a file
    with open(dbPath + 'course_names.txt', 'w') as names_file:
        for name in course_names:
            names_file.write(f"{name}\n")
    
    print("Course acronyms and names have been written to 'course_acronyms.txt' and 'course_names.txt'.")
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")
