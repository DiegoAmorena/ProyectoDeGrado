import requests
import os
from pathlib import Path
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import torch

print("PyTorch version:", torch.__version__)
print("CUDA available:", torch.cuda.is_available())
import whisper  # Import the Whisper library
# Set the base URL and main output path
base_url = "https://open.fing.edu.uy/media/{course}/{course}_{nn}.mp4"
course_acronyms_path = Path("../DB/CoursesNames/course_acronyms.txt")
main_output_path = Path("../DB/Opens")
transcriptions_path = Path("../DB/Transcripciones")  # Path for transcriptions
max_files = 50  # Maximum number of files to download (not used if controlled by classes.txt)
total_max_size = 15 * 1024 * 1024 * 1024  # 15 GB in bytes
current_time = datetime.now().strftime("%Y%m%d%H%M%S")  # More precise timestamp
error_log_path = "../Logs" / f"error_log_{current_time}.txt"

# Load Whisper model
model = whisper.load_model("medium")

def get_folder_size(path):
    """Calculate the total size of files in a given directory."""
    total_size = 0
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            total_size += os.path.getsize(file_path)
    return total_size

def download_video(url, path):
    """Download a video from a URL and save it to a specified path."""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 404:
            with open(error_log_path, "a") as log_file:
                log_file.write(f"Video not found {url}\n")
            return 0  # Skip logging other errors for 404, just note it
        response.raise_for_status()  # Raises an HTTPError for bad responses
        with open(path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return os.path.getsize(path)
    except requests.RequestException as e:
        with open(error_log_path, "a") as log_file:
            log_file.write(f"Failed to download {url}: {str(e)}\n")
        return 0

def transcribe_video(video_path, course_name):
    """Transcribe a video and save the transcript in Spanish and auto-detected languages."""
    try:
        result = model.transcribe(str(video_path))
        text = result['text']
        
        # Determine transcription paths
        spanish_path = transcriptions_path / course_name / "es"
        autodetect_path = transcriptions_path / course_name / "ad"
        spanish_path.mkdir(parents=True, exist_ok=True)
        autodetect_path.mkdir(parents=True, exist_ok=True)
        
        # Save Spanish transcription if detected as Spanish
        if result.get('language') == 'es':
            with open(spanish_path / f"{video_path.stem}.txt", "w") as f:
                f.write(text)
        
        # Always save auto-detection transcription
        with open(autodetect_path / f"{video_path.stem}.txt", "w") as f:
            f.write(text)
    
    except Exception as e:
        with open(error_log_path, "a") as log_file:
            log_file.write(f"Failed to transcribe {video_path}: {str(e)}\n")

def transcribe_audio(model, audio_path, language, output_path):
    """Transcribe audio and save the result to a specified path."""
    result = model.transcribe(audio_path, language=language)
    with open(output_path, 'w') as f:
        f.write(result['text'])

def process_course(course_name, total_downloaded):
    start_time = time.time()
    course_path = main_output_path / course_name
    course_path.mkdir(exist_ok=True)  # Ensure course directory exists

    # Read the classes.txt file to get the list of class numbers to download
    classes_file_path = course_path / "classes.txt"
    if not classes_file_path.exists():
        print(f"No classes.txt found for {course_name}, skipping...")
        return total_downloaded

    with open(classes_file_path, "r") as file:
        class_numbers = [line.strip() for line in file if line.strip().isdigit()]

    folder_size = get_folder_size(course_path)
    file_count = 0

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = []
        for nn in class_numbers:
            formatted_nn = f"{nn:02}"
            video_path = course_path / f"{course_name}_{formatted_nn}.mp4"
            video_url = base_url.format(course=course_name, nn=formatted_nn)

            if video_path.exists():
                print(f"Skipping {video_path}, already downloaded.")
                continue

            if total_downloaded >= total_max_size:
                break

            futures.append(executor.submit(download_video, video_url, video_path))

        for future in as_completed(futures):
            size = future.result()
            if size > 0:
                file_count += 1
                folder_size += size
                total_downloaded += size
                if total_downloaded >= total_max_size:
                    break

                # Transcribe the video in Spanish and auto-detect
                spanish_transcription_path = Path(f"../DB/Transcripciones/{model}/{course_name}/es/{video_path.stem}.txt")
                auto_detect_transcription_path = Path(f"../DB/Transcripciones/{model}/{course_name}/ad/{video_path.stem}.txt")

                # Ensure output directories exist
                spanish_transcription_path.parent.mkdir(parents=True, exist_ok=True)
                auto_detect_transcription_path.parent.mkdir(parents=True, exist_ok=True)

                # Transcribe in Spanish
                transcribe_audio(model, video_path, language="es", output_path=spanish_transcription_path)

                # Transcribe with auto-detection
                transcribe_audio(model, video_path, language=None, output_path=auto_detect_transcription_path)

    end_time = time.time()
    elapsed_time = end_time - start_time
    hours, remainder = divmod(elapsed_time, 3600)
    minutes, seconds = divmod(remainder, 60)
    print(f"Course: {course_name}, Files: {file_count}, Directory size: {folder_size / 1024 / 1024 / 1024:.2f} GB, Time: {int(hours):02}:{int(minutes):02}:{int(seconds):02}")
    return total_downloaded

def main():
    global model
    model = whisper.load_model("medium")  # Load the Whisper model once

    total_downloaded = 0
    with open(course_acronyms_path, "r") as course_file:
        courses = [line.strip() for line in course_file if line.strip()]
    for course_name in courses:
        if total_downloaded >= total_max_size:
            print("Stopping, total size limit exceeded.")
            break
        total_downloaded = process_course(course_name, total_downloaded)

if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()
