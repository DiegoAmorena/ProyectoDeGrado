# Define the path to the folder containing .wav files
$audioFolderPath = "C:\Users\damorena\_Modulos\Facu\ProyectoDeGrado\ProyectoDeGrado\DB\Opens\pln"
$transcriptionOutputFolder = "C:\Users\damorena\_Modulos\Facu\ProyectoDeGrado\ProyectoDeGrado\DB\Transcripciones\pln"

# Ensure the transcription output folder exists
if (-Not (Test-Path $transcriptionOutputFolder)) {
    New-Item -ItemType Directory -Path $transcriptionOutputFolder
}

# Define the model to use
$model = "tiny"

# Loop through each .wav file in the folder
Get-ChildItem -Path $audioFolderPath -Filter "*.wav" | ForEach-Object {
    $audioFile = $_.FullName
    $fileNameWithoutExtension = [System.IO.Path]::GetFileNameWithoutExtension($_.Name)
    $finalOutputPath = Join-Path $transcriptionOutputFolder "$fileNameWithoutExtension`_$model.txt"

    # Start measuring time
    $startTime = Get-Date

    # Construct the whisper command to transcribe the audio
    $whisperCommand = "whisper '$audioFile' --model $model --language es --output_dir '$transcriptionOutputFolder' --output_format txt"

    # Run the whisper command
    Invoke-Expression $whisperCommand

    # End measuring time
    $endTime = Get-Date
    $timeTaken = $endTime - $startTime

    # Rename the generated file to include the model name
    $generatedFilePath = Join-Path $transcriptionOutputFolder "$fileNameWithoutExtension.txt"
    if (Test-Path $generatedFilePath) {
        Rename-Item -Path $generatedFilePath -NewName "$fileNameWithoutExtension`_$model.txt"
    }

    # Print the output path and time taken
    Write-Host "Transcription saved to: $finalOutputPath"
    Write-Host "Time taken for transcription: $($timeTaken.TotalSeconds) seconds"
}

Write-Host "Transcription process completed."
