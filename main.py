import os
import gradio as gr
import whisper as ws
from translate import Translator
from dotenv import dotenv_values
from elevenlabs.client import ElevenLabs
from elevenlabs import VoiceSettings

config = dotenv_values(".env")

ELEVENLABS_APY_KEY = config["ELEVENLABS_APY_KEY"]

def translator(audio_file):
    # Cargar el modelo Whisper

    try:
        model = ws.load_model("base")
        result = model.transcribe(audio_file,language="Spanish",fp16=False)
        transcription = result["text"]
    except Exception as e:
        raise gr.Error(f"Se ha producido un error transcribiendo el texto: {str(e)}")
    
    print(f"texto original: {transcription}")
    
    # Usar Translate

    try:
        en_transcription = Translator(from_lang="es",to_lang="en").translate(transcription)
    except Exception as e:
        raise gr.Error(f"Error usando Translator traduciendo el texto: {str(e)}")
    print(f"texto traducido: {en_transcription}")

    # Generar audio traducido usando Elevenlabs

    try:
        client = ElevenLabs(api_key=ELEVENLABS_APY_KEY)
        
        response = client.text_to_speech.convert(
            voice_id="pNInz6obpgDQGcFmaJgB",  # Adam voice
            optimize_streaming_latency="0",
            output_format="mp3_22050_32",
            text=en_transcription,  # Texto que queremos transformar
            model_id="eleven_turbo_v2",  # use the turbo model for low latency, for other languages use the `eleven_multilingual_v2`
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
            ),
        )

        # Verificar y crear el directorio si no existe
        save_dir = "audios"
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)

        save_file_path = os.path.join(save_dir, "en.mp3")
        with open(save_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)

    except Exception as e:
        raise gr.Error(f"Error generando el audio traducido: {str(e)}")       

    return save_file_path

web = gr.Interface(
    fn=translator,
    inputs=gr.Audio(
        sources=['microphone'],
        type="filepath",
        label="español"
    ),
    outputs=gr.Audio(label="Inglés"),
    title="Traductor de voz",
    description="Traductor de voz con IA en varios idiomas"
)

web.launch()


