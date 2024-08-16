from pathlib import Path

import torch
import whisper


class Transcriber:
    def __init__(
        self, logger, transcription_path="../DB/Transcripciones/", model_name="tiny"
    ):
        self.logger = logger
        self.transcription_path = transcription_path
        self.model_name = model_name

        device = (
            "cuda:0"
            if torch.cuda.is_available()
            else "mps"
            if torch.backends.mps.is_available()
            else "cpu"
        )

        logger.log_message(f"Using device: {device}")

        self.model = whisper.load_model(
            self.model_name,
            device=device,
            in_memory=True,
        )

    def transcribe_video(self, video_path, course_name):
        try:
            video_stem = video_path.stem
            spanish_path = (
                Path(self.transcription_path)
                / course_name
                / "es"
                / f"{video_stem}_{self.model_name}.txt"
            )
            autodetect_path = (
                Path(self.transcription_path)
                / course_name
                / "ad"
                / f"{video_stem}_{self.model_name}.txt"
            )

            if not video_path.exists():
                self.logger.log_message(f"Video file not found: {video_path}")
                return

            if not spanish_path.exists():
                result = self.model.transcribe(str(video_path), language="es")

                with open(spanish_path, "w") as f:
                    f.write(result["text"])
                self.logger.log_message(
                    f"Spanish transcription completed for {video_stem} using model {self.model_name}."
                )
            else:
                self.logger.log_message(
                    f"Spanish transcription already exist for {video_stem}, skipping..."
                )

            if not autodetect_path.exists():
                result = self.model.transcribe(str(video_path))

                with open(autodetect_path, "w") as f:
                    f.write(result["text"])
                self.logger.log_message(
                    f"Auto-detected transcription completed for {video_stem} using model {self.model_name}."
                )
            else:
                self.logger.log_message(
                    f"Auto-detected transcription already exist for {video_stem}, skipping..."
                )

        except Exception as e:
            self.logger.log_message(f"Failed to transcribe {video_path}: {str(e)}")
