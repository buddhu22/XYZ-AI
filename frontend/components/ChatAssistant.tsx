"use client";

import React, { useState, useRef, useEffect } from "react";
import AIAvatar, { AvatarState } from "./AIAvatar";
import { getStoredAuth } from "@/lib/auth";

// 11 Supported languages for Multilingual support
export const SUPPORTED_LANGUAGES = [
  { code: "en", name: "English" },
  { code: "hi", name: "Hindi (हिन्दी)" },
  { code: "ta", name: "Tamil (தமிழ்)" },
  { code: "te", name: "Telugu (తెలుగు)" },
  { code: "mr", name: "Marathi (मराठी)" },
  { code: "bn", name: "Bengali (বাংলা)" },
  { code: "gu", name: "Gujarati (ગુજરાતી)" },
  { code: "pa", name: "Punjabi (ਪੰਜਾਬੀ)" },
  { code: "kn", name: "Kannada (ಕನ್ನಡ)" },
  { code: "ml", name: "Malayalam (മലയാളം)" },
  { code: "ur", name: "Urdu (اردو)" },
];

interface ChatAssistantProps {
  role: string;
  token?: string;
  userName?: string;
  onClose: () => void;
}

interface Message {
  sender: "user" | "ai";
  text: string;
  type: "text" | "voice";
  transcription?: string;
}

export default function ChatAssistant({ role, token: propToken, userName, onClose }: ChatAssistantProps) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState("");
  const [language, setLanguage] = useState("en");
  const [avatarState, setAvatarState] = useState<AvatarState>("IDLE");
  
  // Microphone recording states
  const [isRecording, setIsRecording] = useState(false);
  const [recordingDuration, setRecordingDuration] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<Blob[]>([]);
  const durationIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Audio playback
  const audioPlayerRef = useRef<HTMLAudioElement | null>(null);
  const messagesEndRef = useRef<HTMLDivElement | null>(null);

  // Set default initial greeting
  useEffect(() => {
    const greeting = getGreeting(role);
    setMessages([{ sender: "ai", text: greeting, type: "text" }]);
  }, [role]);

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  // Cleanup timers on unmount
  useEffect(() => {
    return () => {
      if (durationIntervalRef.current) clearInterval(durationIntervalRef.current);
    };
  }, []);

  const getGreeting = (roleName: string) => {
    switch (roleName.toLowerCase()) {
      case "student":
        return "Hello Aarav! Ask me anything about your attendance or schedules.";
      case "parent":
        return "Welcome back! You can check your child's attendance here.";
      case "teacher":
        return "Hello Teacher. You can mark attendance or fetch student summaries.";
      case "principal":
        return "Good day Principal. Ask me for school-wide attendance metrics.";
      default:
        return "Hello! How can I assist you today?";
    }
  };

  // --- Voice Recording Flow ---
  const startRecording = async () => {
    try {
      audioChunksRef.current = [];
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      
      // Select appropriate MIME type
      const options = { mimeType: "audio/webm" };
      const recorder = new MediaRecorder(stream, options);
      
      recorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunksRef.current.push(event.data);
        }
      };

      recorder.onstop = async () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        stream.getTracks().forEach((track) => track.stop()); // Release mic hardware
        await sendVoiceMessage(audioBlob);
      };

      mediaRecorderRef.current = recorder;
      recorder.start(250); // Slice data chunks every 250ms
      setIsRecording(true);
      setAvatarState("LISTENING");
      
      setRecordingDuration(0);
      durationIntervalRef.current = setInterval(() => {
        setRecordingDuration((prev) => prev + 1);
      }, 1000);

    } catch (err) {
      console.error("Microphone access denied:", err);
      setAvatarState("ERROR");
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: "Error: Microphone permission denied. Please allow microphone access in settings.", type: "text" },
      ]);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      if (durationIntervalRef.current) {
        clearInterval(durationIntervalRef.current);
        durationIntervalRef.current = null;
      }
    }
  };

  const sendVoiceMessage = async (audioBlob: Blob) => {
    setAvatarState("THINKING");
    
    // Add local user placeholder message
    const userVoiceMsgIndex = messages.length;
    setMessages((prev) => [
      ...prev,
      { sender: "user", text: "[Voice Input]", type: "voice" },
    ]);

    try {
      // Setup payload matching backend multipart form request
      const formData = new FormData();
      formData.append("audio", audioBlob, "recording.webm");
      formData.append("role", role.toLowerCase());
      formData.append("language", language);
      
      // Sourced from dynamic trusted contexts:
      // Parent: Rajesh Sharma (user_id=5, parent_id=1)
      // Student: Aarav Sharma (user_id=10, student_id=1)
      // Teacher: Amit Kumar (user_id=2, teacher_id=1)
      const user_id_map: Record<string, number> = { student: 10, parent: 5, teacher: 2, principal: 1 };
      const userId = user_id_map[role.toLowerCase()] || 101;
      formData.append("user_id", String(userId));

      const auth = getStoredAuth();
      const authToken = propToken || auth.token;
      const headers: Record<string, string> = {};
      if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
      }

      const response = await fetch("http://127.0.0.1:8000/api/v1/chat/voice", {
        method: "POST",
        headers: headers,
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`Voice server response error: ${response.status}`);
      }

      const data = await response.json();
      
      // Update the user's placeholder message with actual transcription
      setMessages((prev) => {
        const copy = [...prev];
        if (copy[userVoiceMsgIndex]) {
          copy[userVoiceMsgIndex].text = `🎙️ "${data.transcription || "Unclear Speech"}"`;
        }
        return copy;
      });

      // Add AI Response message
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: data.response, type: "text" },
      ]);

      // Playback Speech Synthesis (TTS)
      if (data.audio_base64) {
        playTTS(data.audio_base64);
      } else {
        setAvatarState("IDLE");
      }

    } catch (error) {
      console.error("STT/Voice API call failed:", error);
      setAvatarState("ERROR");
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: "Failed to transcribe or process your voice message. Please check server logs.", type: "text" },
      ]);
    }
  };

  // --- Text Messaging Flow ---
  const sendTextMessage = async () => {
    if (!inputText.trim()) return;
    
    const text = inputText;
    setInputText("");
    setAvatarState("THINKING");

    setMessages((prev) => [...prev, { sender: "user", text, type: "text" }]);

    try {
      const auth = getStoredAuth();
      const authToken = propToken || auth.token;
      const userId = auth.user?.id || 10;

      const headers: Record<string, string> = { "Content-Type": "application/json" };
      if (authToken) {
        headers["Authorization"] = `Bearer ${authToken}`;
      }

      const response = await fetch("http://127.0.0.1:8000/api/v1/chat", {
        method: "POST",
        headers: headers,
        body: JSON.stringify({
          message: text,
          role: role.toLowerCase(),
          user_id: userId,
          language: language,
        }),
      });

      if (!response.ok) {
        throw new Error(`Text response error: ${response.status}`);
      }

      const data = await response.json();
      
      // Add AI text response
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: data.response, type: "text" },
      ]);

      // Optional: TTS audio generation from text endpoint if supported, else back to IDLE
      if (data.audio_base64) {
        playTTS(data.audio_base64);
      } else {
        setAvatarState("IDLE");
      }

    } catch (err) {
      console.error("Text chat failed:", err);
      setAvatarState("ERROR");
      setMessages((prev) => [
        ...prev,
        { sender: "ai", text: "Unable to process text request at this time. Is the FastAPI server running?", type: "text" },
      ]);
    }
  };

  const playTTS = (base64Audio: string) => {
    try {
      const audioUrl = `data:audio/mp3;base64,${base64Audio}`;
      if (audioPlayerRef.current) {
        audioPlayerRef.current.src = audioUrl;
        audioPlayerRef.current.onplay = () => setAvatarState("SPEAKING");
        audioPlayerRef.current.onended = () => setAvatarState("IDLE");
        audioPlayerRef.current.onerror = () => setAvatarState("ERROR");
        audioPlayerRef.current.play();
      }
    } catch (err) {
      console.error("Failed to play TTS audio:", err);
      setAvatarState("ERROR");
    }
  };

  const formatDuration = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s < 10 ? "0" : ""}${s}`;
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-950/80 p-4 backdrop-blur-md">
      {/* Hidden TTS player */}
      <audio ref={audioPlayerRef} className="hidden" />

      {/* Main dialog layout */}
      <div className="relative flex h-[85vh] w-full max-w-2xl flex-col rounded-3xl border border-zinc-800 bg-zinc-900 shadow-2xl overflow-hidden">
        {/* Header */}
        <header className="flex items-center justify-between border-b border-zinc-800 bg-zinc-900/50 px-6 py-4">
          <div className="flex items-center gap-3">
            <span className="flex h-3.5 w-3.5 items-center justify-center rounded-full bg-indigo-500 animate-pulse"></span>
            <div>
              <h2 className="text-sm font-semibold text-zinc-100">XYZ AI Assistant</h2>
              <p className="text-xs text-zinc-400">Authenticated Role: <span className="font-medium text-indigo-400 capitalize">{role}</span></p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {/* Language dropdown select */}
            <select
              value={language}
              onChange={(e) => setLanguage(e.target.value)}
              className="rounded-lg border border-zinc-800 bg-zinc-950 px-3 py-1.5 text-xs text-zinc-300 outline-none focus:border-zinc-700"
            >
              {SUPPORTED_LANGUAGES.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
            <button
              onClick={onClose}
              className="text-zinc-400 hover:text-zinc-100 focus:outline-none"
            >
              ✕
            </button>
          </div>
        </header>

        {/* AI Presentation Layer (Avatar) */}
        <div className="border-b border-zinc-800 bg-zinc-950/20 py-2">
          <AIAvatar state={avatarState} />
        </div>

        {/* Conversation Dialog Messages */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.map((msg, index) => (
            <div
              key={index}
              className={`flex ${msg.sender === "user" ? "justify-end" : "justify-start"}`}
            >
              <div
                className={`max-w-[80%] rounded-2xl px-4 py-3 text-sm shadow-md leading-relaxed ${
                  msg.sender === "user"
                    ? "bg-indigo-600 text-white rounded-br-none"
                    : "bg-zinc-800 text-zinc-200 rounded-bl-none border border-zinc-800"
                }`}
              >
                {msg.text}
              </div>
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>

        {/* Footer Input controls */}
        <footer className="border-t border-zinc-800 bg-zinc-900/50 p-4">
          <div className="flex items-center gap-3">
            {/* Mic record button */}
            {!isRecording ? (
              <button
                type="button"
                onClick={startRecording}
                className="flex h-12 w-12 items-center justify-center rounded-xl bg-zinc-800 text-zinc-200 hover:bg-zinc-700 hover:text-zinc-100 transition shadow"
                title="Speak to Assistant"
              >
                🎙️
              </button>
            ) : (
              <button
                type="button"
                onClick={stopRecording}
                className="flex h-12 w-12 items-center justify-center rounded-xl bg-red-600 text-white animate-pulse shadow-lg"
                title="Stop Recording"
              >
                🛑
              </button>
            )}

            {/* Input field */}
            <input
              type="text"
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && sendTextMessage()}
              disabled={isRecording}
              placeholder={isRecording ? `Recording... (${formatDuration(recordingDuration)})` : "Type a message..."}
              className="flex-1 rounded-xl border border-zinc-800 bg-zinc-950 px-4 py-3 text-sm text-zinc-300 placeholder-zinc-500 outline-none focus:border-zinc-700 disabled:bg-zinc-950/50 disabled:cursor-not-allowed"
            />

            <button
              onClick={sendTextMessage}
              disabled={!inputText.trim() || isRecording}
              className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white hover:bg-indigo-500 transition disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Send
            </button>
          </div>
        </footer>
      </div>
    </div>
  );
}
