import os
import numpy as np
import gradio as gr
import assemblyai as aai
from translate import Translator
import uuid
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from pathlib import Path
from dotenv import load_dotenv


# Load environment variables from a .env file
load_dotenv()

# Assign API keys and Voice ID from environment variables
ASSEMBLYAI_API_KEY = os.getenv("0a9033e316144a1eb88daf3a9371f290")  # Your AssemblyAI API key
ELEVENLABS_API_KEY = os.getenv("sk_0d4ab8818a5d158532429fc9874f25b9d6d3f10542ca703e")  # Your ElevenLabs API key
VOICE_ID = os.getenv("pNInz6obpgDQGcFmaJgB")  # Your ElevenLabs Voice ID

# Function to transcribe audio using AssemblyAI
def transcribe_audio(audio_file):
    aai.settings.api_key = "0a9033e316144a1eb88daf3a9371f290"
    transcriber = aai.Transcriber()
    transcript = transcriber.transcribe(audio_file)
    return transcript

# Function to translate text
def translate_text(text: str) -> str:
    languages = ["en", "sv", "de", "es", "ja", "ar"]
    list_translations = []

    for lan in languages:
        translator = Translator(from_lang="en", to_lang=lan)
        translation = translator.translate(text)
        list_translations.append(translation)

    return list_translations

# Function to generate speech using ElevenLabs
def text_to_speech(text: str) -> str:
    client = ElevenLabs(api_key="sk_0d4ab8818a5d158532429fc9874f25b9d6d3f10542ca703e")  # Pass your ElevenLabs API key
    response = client.text_to_speech.convert(
        voice_id="pNInz6obpgDQGcFmaJgB",  # Pass your ElevenLabs voice ID
        optimize_streaming_latency="0",
        output_format="mp3_22050_32",
        text=text,
        model_id="eleven_multilingual_v2",
        voice_settings=VoiceSettings(
            stability=0.5,
            similarity_boost=0.8,
            style=0.5,
            use_speaker_boost=True,
        ),
    )

    save_file_path = f"{uuid.uuid4()}.mp3"
    with open(save_file_path, "wb") as f:
        for chunk in response:
            if chunk:
                f.write(chunk)
    print(f"{save_file_path}: A new audio file was saved successfully!")
    return save_file_path

# Function for voice-to-voice translation
def voice_to_voice(audio_file):
    transcript = transcribe_audio(audio_file)

    if transcript.status == aai.TranscriptStatus.error:
        raise gr.Error(transcript.error)
    else:
        transcript = transcript.text

    list_translations = translate_text(transcript)
    generated_audio_paths = []

    for translation in list_translations:
        translated_audio_file_name = text_to_speech(translation)
        path = Path(translated_audio_file_name)
        generated_audio_paths.append(path)

    return generated_audio_paths[0], generated_audio_paths[1], generated_audio_paths[2], generated_audio_paths[3], generated_audio_paths[4], generated_audio_paths[5], list_translations[0], list_translations[1], list_translations[2], list_translations[3], list_translations[4], list_translations[5]

# Gradio interface to upload or record audio
input_audio = gr.Audio(
    sources=["upload", "microphone"],  # Allow both file upload and microphone input
    type="filepath",
    show_download_button=True,
    waveform_options=gr.WaveformOptions(
        waveform_color="#01C6FF",
        waveform_progress_color="#0066B4",
        skip_length=2,
        show_controls=False,
    ),
)

with gr.Blocks(css="styles.css") as demo:
    gr.Markdown("## Record yourself in English and immediately receive voice translations.")
    with gr.Row():
        with gr.Column():
            audio_input = gr.Audio(sources=["microphone", "upload"],
                                   type="filepath",
                                   show_download_button=True,
                                   waveform_options=gr.WaveformOptions(
                                       waveform_color="#01C6FF",
                                       waveform_progress_color="#0066B4",
                                       skip_length=2,
                                       show_controls=False,
                                   ))
            with gr.Row():
                submit = gr.Button("Submit", variant="primary")
                btn = gr.ClearButton(audio_input, "Clear")
                btn.click(lambda: audio_input, None)

    with gr.Row():
        with gr.Group() as English:
            tr_output = gr.Audio(label="English", interactive=False)
            tr_text = gr.Markdown()

        with gr.Group() as Swedish:
            sv_output = gr.Audio(label="Swedish", interactive=False)
            sv_text = gr.Markdown()

        with gr.Group() as German:
            ru_output = gr.Audio(label="German", interactive=False)
            ru_text = gr.Markdown()

    with gr.Row():
        with gr.Group():
            de_output = gr.Audio(label="Spanish", interactive=False)
            de_text = gr.Markdown()

        with gr.Group():
            es_output = gr.Audio(label="Japanese", interactive=False)
            es_text = gr.Markdown()

        with gr.Group():
            jp_output = gr.Audio(label="Arabic", interactive=False)
            jp_text = gr.Markdown()

    output_components = [ru_output, tr_output, sv_output, de_output, es_output, jp_output, ru_text, tr_text, sv_text, de_text, es_text, jp_text]
    submit.click(fn=voice_to_voice, inputs=audio_input, outputs=output_components, show_progress=True)

if __name__ == "__main__":
    demo.launch()