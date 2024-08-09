import whisper
from pathlib import Path

class Transcriber:
    def __init__(self, logger, transcription_path="../DB/Transcriptions/"):
        self.logger = logger
        self.transcription_path = transcription_path
        self.model_name = "tiny"
        self.model = whisper.load_model(self.model_name)

    def transcribe_video(self, video_path, course_name):
        try:
            video_stem = video_path.stem  # Extract the file name without extension
            spanish_path = Path(self.transcription_path) / course_name / "es" / f"{video_stem}_{self.model_name}.txt"
            autodetect_path = Path(self.transcription_path) / course_name / "ad" / f"{video_stem}_{self.model_name}.txt"

            # Check if the transcription files already exist
            if spanish_path.exists() and autodetect_path.exists():
                self.logger.log_message(f"Transcriptions for {video_stem} using model {self.model_name} already exist. Skipping transcription.")
                return

            # Create directories if they do not exist
            spanish_path.parent.mkdir(parents=True, exist_ok=True)
            autodetect_path.parent.mkdir(parents=True, exist_ok=True)

            # Perform the transcription
            result = self.model.transcribe(str(video_path))
            text = result['text']

            # Save the transcription in the appropriate path
            if result.get('language') == 'es':
                with open(spanish_path, "w") as f:
                    f.write(text)

            with open(autodetect_path, "w") as f:
                f.write(text)

            self.logger.log_message(f"Transcription completed for {video_stem} using model {self.model_name}.")

        except Exception as e:
            self.logger.log_message(f"Failed to transcribe {video_path}: {str(e)}")
