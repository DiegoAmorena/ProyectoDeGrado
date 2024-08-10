from pathlib import Path
import os
from Logger import Logger

class ClassValidation:
    
    def is_download_complete(self, file_path):
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
    def validate_existing_file(self, video_path, expected_size):
        """Validate that a previously downloaded file matches the expected size and is playable."""
        actual_size = os.path.getsize(video_path)
        if actual_size != expected_size:
            self.logger.log_message(f"File {video_path} size mismatch: expected {expected_size / 1024 / 1024 / 1024:.2f} GB, got {actual_size / 1024 / 1024 / 1024:.2f} GB")
            return False
        if not self.is_download_complete(video_path):
            self.logger.log_message(f"File {video_path} is not playable.")
            return False
        return True