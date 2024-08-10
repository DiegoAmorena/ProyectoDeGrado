from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from ClassDownloader import ClassDownloader
import os
from Logger import Logger

class CourseDownloader:
    def __init__(self, logger, transcriber, base_url="https://open.fing.edu.uy/media/{course}/{course}_{nn}.mp4", db_path="../DB/Opens/", total_max_size=15 * 1024 * 1024 * 1024):
        self.logger = logger
        self.base_url = base_url
        self.transcriber = transcriber
        self.db_path = db_path
        self.total_max_size = total_max_size
        self.class_downloader = ClassDownloader(transcriber,logger)

    def get_folder_size(self, path):
        total_size = 0
        for file in os.listdir(path):
            file_path = os.path.join(path, file)
            if os.path.isfile(file_path):
                total_size += os.path.getsize(file_path)
        return total_size

    def process_course(self, course_name):
        total_downloaded = 0
        course_path = Path(self.db_path) / course_name
        course_path.mkdir(exist_ok=True)
        classes_file_path = course_path / "classes.txt"

        if not classes_file_path.exists():
            self.logger.log_message(f"No classes.txt found for {course_name}, skipping...")
            return

        with open(classes_file_path, "r") as file:
            class_numbers = [line.strip() for line in file if line.strip().isdigit()]

        folder_size = self.get_folder_size(course_path)
        file_count = 0

        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = []
            for nn in class_numbers:
                formatted_nn = nn.zfill(2)
                video_path = course_path / f"{course_name}_{formatted_nn}.mp4"
                video_url = self.base_url.format(course=course_name, nn=formatted_nn)

                # Initialize expected_size to a default value
                expected_size = 0
                try:
                    response = requests.head(video_url)
                    expected_size = int(response.headers.get('content-length', 0))
                except Exception as e:
                    self.logger.log_message(f"Failed to get expected size for {video_url}: {str(e)}")
                    continue  # Skip this video if we can't determine the expected size

                if total_downloaded >= self.total_max_size:
                    break

                futures.append(executor.submit(self.class_downloader.process_class, video_url, video_path, expected_size, course_name))

            for future in as_completed(futures):
                future.result()
                file_count += 1
                total_downloaded = self.get_folder_size(course_path)  # Recalculate total size
                if total_downloaded >= self.total_max_size:
                    break

        self.logger.log_message(f"Course: {course_name}, Files: {file_count}, Directory size: {folder_size / 1024 / 1024 / 1024:.2f} GB")
