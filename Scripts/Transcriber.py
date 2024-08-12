import whisper
from pathlib import Path

class Transcriber:
    def __init__(self, logger, transcription_path="../DB/Transcripciones/", model_name="tiny"):
        self.logger = logger
        self.transcription_path = transcription_path
        self.model_name = model_name
        self.model = whisper.load_model(self.model_name)

    def transcribe_video(self, video_path, course_name):
        try:
            video_stem = video_path.stem  # Extract the file name without extension
            spanish_path = Path(self.transcription_path) / course_name / "es" / f"{video_stem}_{self.model_name}.txt"
            autodetect_path = Path(self.transcription_path) / course_name / "ad" / f"{video_stem}_{self.model_name}.txt"

            # Ensure file exists before processing
            if not video_path.exists():
                self.logger.log_message(f"File not found: {video_path}")
                return

            # Skip if transcriptions already exist
            if spanish_path.exists() and autodetect_path.exists():
                self.logger.log_message(f"Transcriptions already exist for {video_stem}, skipping...")
                return

            self.logger.log_message(f"Starting transcription for {video_stem} using model {self.model_name}.")

            # Perform the transcription
            #result = self.model.transcribe(str(video_path))
            #text = result['text']
            #detected_language = result.get('language')

            # Handle Spanish transcription
            #if detected_language == 'es' and not spanish_path.exists():
                #with open(spanish_path, "w") as f:
                    #f.write(text)
                #self.logger.log_message(f"Spanish transcription completed for {video_stem} using model {self.model_name}.")

            # Handle auto-detected transcription
            #if not autodetect_path.exists():
                #with open(autodetect_path, "w") as f:
                    #f.write(text)
                #self.logger.log_message(f"Auto-detected transcription completed for {video_stem} using model {self.model_name}.")

        except Exception as e:
            self.logger.log_message(f"Failed to transcribe {video_path}: {str(e)}")

