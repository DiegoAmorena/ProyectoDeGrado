from pathlib import Path
from CourseScraper import CourseScraper
from VideoDownloader import VideoDownloader
from Logger import Logger
from ClassScraper import ClassScraper
from Transcriber import Transcriber

def main():
    logger = Logger()

    # Step 1: Scrape Courses and Classes
    course_scraper = CourseScraper(logger)
    class_scraper = ClassScraper(logger)
    
    course_acronyms_path = Path("../DB/CoursesNames/course_acronyms.txt")

    # Check if CourseScraper or ClassScraper need to run
    if course_scraper.should_run() or class_scraper.should_run():
        course_scraper.fetch_courses()
        
        if course_acronyms_path.exists():
            with open(course_acronyms_path, 'r') as file:
                course_acronyms = [line.strip() for line in file if line.strip()]

            for acronym in course_acronyms:
                class_scraper.save_classes_to_file(acronym)
        else:
            logger.log_message(f"Course acronyms file not found at {course_acronyms_path}. Aborting process.")
            return  # Exit the script if the acronyms file is missing

        # After successfully scraping, update the timestamp for both scrapers
        course_scraper.update_timestamp()
        class_scraper.update_timestamp()
    else:
        logger.log_message("CourseScraper and ClassScraper skipped as they were already run within the last week.")

    # Step 2: Initialize Transcriber
    transcriber = Transcriber(logger)

    # Step 3: Download and Process Videos
    video_downloader = VideoDownloader(logger, transcriber)

    if course_acronyms_path.exists():
        with open(course_acronyms_path, 'r') as file:
            course_acronyms = [line.strip() for line in file if line.strip()]

        for acronym in course_acronyms:
            video_downloader.process_course(acronym)

if __name__ == "__main__":
    main()
