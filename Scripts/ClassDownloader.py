import requests
import os
from pathlib import Path
import cv2

class ClassDownloader:
    def __init__(self, transcriber, logger, validation_log_file="../DB/validation_test_pass.txt"):
        self.logger = logger
        self.transcriber = transcriber
        self.validation_log_file = validation_log_file
        self.validation_log_path = Path(self.validation_log_file)

    def load_validation_log(self):
        """Load the validation log file into a set for quick lookup."""
        if self.validation_log_path.exists():
            with open(self.validation_log_path, 'r') as f:
                return set(line.strip() for line in f)
        return set()

    def log_validation_pass(self, video_path):
        """Log the video path in the validation log file."""
        with open(self.validation_log_path, 'a') as f:
            f.write(f"{video_path}\n")

    def validate_video_file(self, video_path, expected_size):
        """Validate that a previously downloaded file matches the expected size and is playable."""
        actual_size = os.path.getsize(video_path)
        if actual_size != expected_size:
            self.logger.log_message(f"File {video_path} size mismatch: expected {expected_size / 1024 / 1024 / 1024:.2f} GB, got {actual_size / 1024 / 1024 / 1024:.2f} GB")
            return False
        if not self.is_download_complete(video_path):
            self.logger.log_message(f"File {video_path} is not playable.")
            return False
        return True

    def download_video(self, url, path, expected_size):
        """Download or resume a video from a URL and save it to a specified path."""
        try:
            headers = {}
            existing_file_size = 0

            if path.exists():
                existing_file_size = os.path.getsize(path)
                if existing_file_size > 0:
                    if existing_file_size < expected_size:
                        headers = {'Range': f'bytes={existing_file_size}-'}
                        self.logger.log_message(f"Resuming download for {path} at byte {existing_file_size}")
                    else:
                        self.logger.log_message(f"Existing file size {existing_file_size / 1024 / 1024 / 1024:.2f} GB is greater than or equal to expected {expected_size / 1024 / 1024 / 1024:.2f} GB. Redownloading...")
                        os.remove(path)

            response = requests.get(url, stream=True, headers=headers)
            if response.status_code in [200, 206]:
                with open(path, 'ab' if existing_file_size > 0 else 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                actual_size = os.path.getsize(path)
                return actual_size
            else:
                self.logger.log_message(f"Failed to download {url}. Status code: {response.status_code}")
                return 0
        except requests.RequestException as e:
            self.logger.log_message(f"Failed to download {url}: {str(e)}")
            return 0

    def is_download_complete(self, file_path):
        """Check if the downloaded file is complete and playable."""
        try:
            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return False
            ret, _ = cap.read()
            cap.release()
            return ret
        except Exception as e:
            self.logger.log_message(f"Error checking playability of {file_path}: {str(e)}")
            return False

    def process_class(self, video_url, video_path, expected_size, course_name):
        validation_log = self.load_validation_log()

        # Check if this video has already passed validation
        if str(video_path) in validation_log:
            self.logger.log_message(f"Skipping validation for {video_path}, already passed previously.")
            self.transcriber.transcribe_video(video_path, course_name)
            return

        # If the video exists, validate it
        if video_path.exists():
            if not self.validate_video_file(video_path, expected_size):
                self.logger.log_message(f"File {video_path} failed validation, redownloading.")
                os.remove(video_path)
            else:
                self.logger.log_message(f"File {video_path} passed validation checks.")
                self.log_validation_pass(video_path)
                self.transcriber.transcribe_video(video_path, course_name)
                return

        # Download the video if it hasn't been validated
        #actual_size = self.download_video(video_url, video_path, expected_size)
        #if actual_size > 0:
        #    if not self.is_download_complete(video_path):
        #        self.logger.log_message(f"File {video_path} is not playable, skipping transcription.")
        #        return
        #    self.log_validation_pass(video_path)
            #self.transcriber.transcribe_video(video_path, course_name)
