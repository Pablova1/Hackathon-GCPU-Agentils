import requests
import base64
import time
from fastapi import HTTPException, UploadFile
from app.core.config import GOOGLE_API_KEY, logger
from app.models.chatbot_model import TranscriptResponse

async def speech_to_text_service(audio: UploadFile) -> TranscriptResponse:
    """
    Convertit un fichier audio en texte via Google Speech-to-Text API
    Version simplifiée sans conversion complexe
    """
    start_time = time.time()
    
    try:
        logger.info(f"🎤 Réception fichier audio: {audio.filename} ({audio.content_type})")
        
        # Validation du fichier
        if not audio.content_type or not audio.content_type.startswith('audio/'):
            logger.warning(f"⚠️ Type de fichier invalide: {audio.content_type}")
            raise HTTPException(status_code=400, detail="Le fichier doit être un fichier audio")
        
        # Lire le contenu du fichier audio
        audio_content = await audio.read()
        file_size = len(audio_content)
        logger.info(f"📁 Taille du fichier: {file_size} bytes")
        
        if file_size == 0:
            logger.warning("⚠️ Fichier audio vide")
            raise HTTPException(status_code=400, detail="Le fichier audio est vide")
        
        if file_size > 10 * 1024 * 1024:  # 10MB limit
            logger.warning(f"⚠️ Fichier trop volumineux: {file_size} bytes")
            raise HTTPException(status_code=400, detail="Le fichier audio est trop volumineux (max 10MB)")
        
        # Configuration simplifiée selon le type de fichier
        audio_base64 = base64.b64encode(audio_content).decode('utf-8')
        
        if audio.content_type == 'audio/webm' or (audio.filename and audio.filename.endswith('.webm')):
            # Configuration optimale pour WebM/Opus
            config = {
                "encoding": "WEBM_OPUS",
                "sampleRateHertz": 48000,
                "languageCode": "fr-FR",
                "model": "latest_short",
                "enableAutomaticPunctuation": True
            }
            logger.info("🔧 Configuration WebM/Opus")
        else:
            # Configuration générique pour autres formats
            config = {
                "encoding": "LINEAR16",
                "sampleRateHertz": 16000,
                "languageCode": "fr-FR",
                "model": "latest_short",
                "enableAutomaticPunctuation": True
            }
            logger.info("🔧 Configuration générique")
        
        # Appel API Google Speech-to-Text
        url = f"https://speech.googleapis.com/v1/speech:recognize?key={GOOGLE_API_KEY}"
        
        payload = {
            "config": config,
            "audio": {"content": audio_base64}
        }
        
        headers = {"Content-Type": "application/json"}
        
        logger.info(f"📦 Taille payload: {len(audio_base64)} caractères base64")
        logger.info("🌐 Appel API Speech-to-Text...")
        
        api_start = time.time()
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        api_latency = (time.time() - api_start) * 1000
        
        logger.info(f"📡 Réponse API: {response.status_code} (latence: {api_latency:.0f}ms)")
        
        if response.status_code == 200:
            data = response.json()
            
            if "results" in data and len(data["results"]) > 0:
                result = data["results"][0]["alternatives"][0]
                transcript = result["transcript"]
                confidence = result.get("confidence", 0.0)
                
                total_latency = (time.time() - start_time) * 1000
                logger.info(f"✅ Transcription réussie: '{transcript}' (conf: {confidence:.2f})")
                
                return TranscriptResponse(
                    transcript=transcript,
                    text=transcript,
                    confidence=confidence,
                    latency_ms=int(total_latency),
                    api_latency_ms=int(api_latency),
                    model_used=config.get('model', 'unknown')
                )
            else:
                logger.warning("⚠️ Aucun résultat de transcription")
                return TranscriptResponse(
                    transcript="",
                    text="", 
                    confidence=0.0, 
                    error="Aucun texte détecté dans l'audio",
                    latency_ms=int((time.time() - start_time) * 1000)
                )
        else:
            error_detail = response.text
            logger.error(f"❌ Erreur API Speech: {response.status_code} - {error_detail}")
            raise HTTPException(
                status_code=response.status_code, 
                detail=f"Erreur API Speech-to-Text: {error_detail}"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        total_latency = (time.time() - start_time) * 1000
        logger.error(f"❌ Erreur Speech-to-Text: {e} (après {total_latency:.0f}ms)")
        raise HTTPException(
            status_code=500, 
            detail=f"Erreur lors de la transcription audio: {str(e)}"
        )