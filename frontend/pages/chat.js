import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '../hooks/useAuth';
import NavigationFooter from '../components/NavigationFooter';
import styles from '../styles/Chat.module.css';

export default function ChatPage() {
  const router = useRouter();
  const { isAuthenticated, isLoading, userId, logout } = useAuth();
  
  // États pour la gestion du chat
  const [messages, setMessages] = useState([
    {
      id: '1',
      text: 'Hello! How can I help you today?\nDo you need nutrition advice?\nWould you like to share something?',
      sender: 'bot',
      timestamp: new Date()
    }
  ]);
  const [inputText, setInputText] = useState('');
  const [isLoadingResponse, setIsLoadingResponse] = useState(false);

  // États pour les modes d'interface
  const [currentMode, setCurrentMode] = useState('text'); // 'text' | 'voice'
  const [sphereState, setSphereState] = useState('listening'); // 'listening' | 'recording' | 'processing'
  const [voiceConversation, setVoiceConversation] = useState([]); // Conversation vocale temporaire

  // États pour Speech-to-Text
  const [isRecording, setIsRecording] = useState(false);
  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);

  // États pour Text-to-Speech  
  const [isSpeaking, setIsSpeaking] = useState(false);

  // Référence pour auto-scroll
  const messagesEndRef = useRef(null);

  // Vérifier l'authentification
  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/welcome');
    }
  }, [isLoading, isAuthenticated, router]);

  // Auto-scroll vers le bas
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Nettoyage des ressources audio au démontage
  useEffect(() => {
    return () => {
      if (isRecording) {
        stopVoiceRecording();
      }
      stopSpeaking();
    };
  }, []);

  const handleLogout = () => {
    logout();
  };

  const handleBackClick = () => {
    router.push('/');
  };

  // Fonction d'envoi de message
  const sendMessage = async (text) => {
    if (!text.trim()) return;

    const userMessage = {
      id: Date.now().toString(),
      text: text.trim(),
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoadingResponse(true);

    // Ajouter un message temporaire pour indiquer que l'assistant réfléchit
    const thinkingMessage = {
      id: 'thinking',
      text: 'Thinking...',
      sender: 'bot',
      timestamp: new Date()
    };
    setMessages(prev => [...prev, thinkingMessage]);

    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: text.trim() })
      });

      if (!response.ok) {
        throw new Error('Network error');
      }

      const data = await response.json();
      
      const botMessage = {
        id: (Date.now() + 1).toString(),
        text: data.response,
        sender: 'bot',
        timestamp: new Date()
      };

      // Remplacer le message "thinking" par la vraie réponse
      setMessages(prev => {
        const withoutThinking = prev.filter(msg => msg.id !== 'thinking');
        return [...withoutThinking, botMessage];
      });
      
      // En mode vocal, ajouter aussi à la conversation vocale
      if (currentMode === 'voice') {
        setVoiceConversation(prev => [...prev, botMessage]);
      }

      // Text-to-Speech pour la réponse du bot (uniquement en mode vocal)
      if (data.response && currentMode === 'voice') {
        speakText(data.response);
      }

    } catch (error) {
      // En cas d'erreur, enlever le message "thinking"
      setMessages(prev => prev.filter(msg => msg.id !== 'thinking'));
      console.error('Error:', error);
      const errorMessage = {
        id: (Date.now() + 1).toString(),
        text: 'Sorry, an error occurred. Please try again.',
        sender: 'bot',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoadingResponse(false);
    }
  };

  // Gestion de l'envoi par formulaire
  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputText);
    setInputText('');
  };

  // Text-to-Speech
  const speakText = (text) => {
    if ('speechSynthesis' in window) {
      // Arrêter toute synthèse en cours
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'en-US';
      utterance.rate = 0.9;
      utterance.pitch = 1;
      
      utterance.onstart = () => setIsSpeaking(true);
      utterance.onend = () => setIsSpeaking(false);
      utterance.onerror = () => setIsSpeaking(false);
      
      window.speechSynthesis.speak(utterance);
    }
  };

  // Arrêter TTS
  const stopSpeaking = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  // Passer en mode vocal
  const enterVoiceMode = () => {
    console.log('🎙️ Voice mode activated');
    setCurrentMode('voice');
    setSphereState('listening');
    setVoiceConversation([]); // Réinitialiser la conversation vocale
    
    // Message de bienvenue vocal
    setTimeout(() => {
      speakText("Voice mode activated. Click on the sphere to start speaking.");
    }, 500);
  };

  // Quitter le mode vocal et revenir au mode texte
  const exitVoiceMode = () => {
    // Arrêter toute synthèse en cours
    stopSpeaking();
    
    // Arrêter l'enregistrement si en cours
    if (isRecording) {
      stopVoiceRecording();
    }
    
    // Ajouter la conversation vocale aux messages principaux
    if (voiceConversation.length > 0) {
      setMessages(prev => [...prev, ...voiceConversation]);
    }
    
    setCurrentMode('text');
    setVoiceConversation([]);
    setSphereState('listening');
  };

  // Gérer le clic sur la sphère
  const handleSphereClick = () => {
    if (sphereState === 'listening') {
      // L'IA parlait, on l'interrompt et on commence l'enregistrement
      stopSpeaking();
      setSphereState('recording');
      startVoiceRecording();
    } else if (sphereState === 'recording') {
      // On arrête l'enregistrement et on traite
      setSphereState('processing');
      stopVoiceRecording();
    }
  };

  // Commencer l'enregistrement vocal
  const startVoiceRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioChunksRef.current = [];

      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      mediaRecorderRef.current = mediaRecorder;

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: 'audio/webm' });
        await processVoiceMessage(audioBlob);
        
        // Arrêter le stream
        stream.getTracks().forEach(track => track.stop());
      };

      mediaRecorder.start(100);
      setIsRecording(true);
    } catch (error) {
      console.error('Microphone error:', error);
      setSphereState('listening');
    }
  };

  // Arrêter l'enregistrement vocal
  const stopVoiceRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
    }
  };

  // Traiter le message vocal
  const processVoiceMessage = async (audioBlob) => {
    try {
      // Étape 1: Transcription
      const formData = new FormData();
      formData.append('audio', audioBlob, 'audio.webm');

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/stt`, {
        method: 'POST',
        body: formData
      });

      if (!response.ok) {
        throw new Error('STT error');
      }

      const data = await response.json();
      
      if (data.transcript && data.transcript.trim()) {
        // Ajouter le message utilisateur à la conversation vocale
        const userMessage = {
          id: Date.now().toString(),
          text: data.transcript,
          sender: 'user',
          timestamp: new Date()
        };
        setVoiceConversation(prev => [...prev, userMessage]);

        // Étape 2: Obtenir la réponse du chatbot
        const chatResponse = await fetch(`${apiUrl}/chat`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ message: data.transcript })
        });

        if (chatResponse.ok) {
          const chatData = await chatResponse.json();
          
          // Ajouter la réponse du bot à la conversation vocale
          const botMessage = {
            id: (Date.now() + 1).toString(),
            text: chatData.response,
            sender: 'bot',
            timestamp: new Date()
          };
          setVoiceConversation(prev => [...prev, botMessage]);

          // Synthèse vocale de la réponse
          setSphereState('listening');
          speakText(chatData.response);
        }
      } else {
        setSphereState('listening');
      }
    } catch (error) {
      console.error('Voice processing error:', error);
      setSphereState('listening');
    }
  };

  if (isLoading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>
          <div className={styles.spinner}></div>
          <p>Loading...</p>
        </div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      {/* Header */}
      <header className={styles.header}>
        <button className={styles.backButton} onClick={handleBackClick}>
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>
        <h1 className={styles.title}>AI Assistant</h1>
        <button className={styles.logoutButton} onClick={handleLogout} title="Logout">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
            <polyline points="16 17 21 12 16 7"/>
            <line x1="21" y1="12" x2="9" y2="12"/>
          </svg>
        </button>
      </header>

      {/* Main content */}
      <main className={styles.main}>
        {currentMode === 'text' ? (
          /* Mode texte */
          <>
            {/* Messages */}
            <div className={styles.messagesContainer}>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`${styles.message} ${message.sender === 'user' ? styles.userMessage : styles.botMessage}`}
                >
                  <div className={styles.messageContent}>
                    <div className={styles.messageText}>
                      {message.text.split('\n').map((line, i) => (
                        <span key={i}>
                          {line}
                          {i < message.text.split('\n').length - 1 && <br />}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>

            {/* Input form */}
            <form onSubmit={handleSubmit} className={styles.inputForm}>
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                placeholder="Type your message..."
                className={styles.input}
                disabled={isLoadingResponse}
              />
              <button
                type="submit"
                className={styles.sendButton}
                disabled={isLoadingResponse || !inputText.trim()}
              >
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                  <line x1="22" y1="2" x2="11" y2="13"></line>
                  <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
                </svg>
              </button>
            </form>

            {/* Voice mode button */}
            <button className={styles.voiceModeButton} onClick={enterVoiceMode}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"></path>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"></path>
                <line x1="12" y1="19" x2="12" y2="23"></line>
                <line x1="8" y1="23" x2="16" y2="23"></line>
              </svg>
              <span>Voice Mode</span>
            </button>
          </>
        ) : (
          /* Mode vocal */
          <div className={styles.voiceModeContainer}>
            {/* Exit voice mode button */}
            <button className={styles.exitVoiceButton} onClick={exitVoiceMode}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>

            {/* Animated sphere */}
            <div className={styles.sphereContainer}>
              <div
                className={`${styles.sphere} ${styles[sphereState]}`}
                onClick={handleSphereClick}
              >
                <div className={styles.sphereInner}></div>
              </div>
              <p className={styles.sphereStatus}>
                {sphereState === 'listening' && 'Listening...'}
                {sphereState === 'recording' && 'Recording...'}
                {sphereState === 'processing' && 'Processing...'}
              </p>
            </div>

            {/* Voice conversation messages */}
            {voiceConversation.length > 0 && (
              <div className={styles.voiceMessages}>
                {voiceConversation.map((message) => (
                  <div
                    key={message.id}
                    className={`${styles.voiceMessage} ${message.sender === 'user' ? styles.userVoiceMessage : styles.botVoiceMessage}`}
                  >
                    {message.text}
                  </div>
                ))}
              </div>
            )}
          </div>
        )}
      </main>

      {/* Footer avec navigation */}
      <NavigationFooter />
    </div>
  );
}
