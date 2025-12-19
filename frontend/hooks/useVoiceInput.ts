/**
 * Voice Input Hook
 * 
 * Uses Web Speech API for voice-to-text input
 * Supports English and Urdu voice commands
 */

"use client";

import { useState, useEffect, useCallback, useRef } from "react";

// Web Speech API type declarations
interface SpeechRecognitionEvent extends Event {
    resultIndex: number;
    results: SpeechRecognitionResultList;
}

interface SpeechRecognitionResultList {
    length: number;
    item(index: number): SpeechRecognitionResult;
    [index: number]: SpeechRecognitionResult;
}

interface SpeechRecognitionResult {
    isFinal: boolean;
    length: number;
    item(index: number): SpeechRecognitionAlternative;
    [index: number]: SpeechRecognitionAlternative;
}

interface SpeechRecognitionAlternative {
    transcript: string;
    confidence: number;
}

interface SpeechRecognitionErrorEvent extends Event {
    error: string;
    message: string;
}

interface SpeechRecognition extends EventTarget {
    continuous: boolean;
    interimResults: boolean;
    lang: string;
    onstart: ((this: SpeechRecognition, ev: Event) => void) | null;
    onend: ((this: SpeechRecognition, ev: Event) => void) | null;
    onresult: ((this: SpeechRecognition, ev: SpeechRecognitionEvent) => void) | null;
    onerror: ((this: SpeechRecognition, ev: SpeechRecognitionErrorEvent) => void) | null;
    start(): void;
    stop(): void;
    abort(): void;
}

interface SpeechRecognitionConstructor {
    new(): SpeechRecognition;
}

declare global {
    interface Window {
        SpeechRecognition?: SpeechRecognitionConstructor;
        webkitSpeechRecognition?: SpeechRecognitionConstructor;
    }
}

interface VoiceInputOptions {
    language?: string;
    continuous?: boolean;
    interimResults?: boolean;
    onResult?: (transcript: string, isFinal: boolean) => void;
    onError?: (error: string) => void;
}

interface VoiceInputState {
    isListening: boolean;
    isSupported: boolean;
    transcript: string;
    error: string | null;
}

export function useVoiceInput(options: VoiceInputOptions = {}) {
    const {
        language = "en-US",
        continuous = false,
        interimResults = true,
        onResult,
        onError,
    } = options;

    const [state, setState] = useState<VoiceInputState>({
        isListening: false,
        isSupported: false,
        transcript: "",
        error: null,
    });

    const recognitionRef = useRef<SpeechRecognition | null>(null);

    useEffect(() => {
        // Check for browser support
        const SpeechRecognition =
            (window as unknown as { SpeechRecognition?: typeof window.SpeechRecognition }).SpeechRecognition ||
            (window as unknown as { webkitSpeechRecognition?: typeof window.SpeechRecognition }).webkitSpeechRecognition;

        if (SpeechRecognition) {
            setState((prev) => ({ ...prev, isSupported: true }));
            recognitionRef.current = new SpeechRecognition();

            const recognition = recognitionRef.current;
            recognition.continuous = continuous;
            recognition.interimResults = interimResults;
            recognition.lang = language;

            recognition.onstart = () => {
                setState((prev) => ({ ...prev, isListening: true, error: null }));
            };

            recognition.onend = () => {
                setState((prev) => ({ ...prev, isListening: false }));
            };

            recognition.onresult = (event: SpeechRecognitionEvent) => {
                let finalTranscript = "";
                let interimTranscript = "";

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const result = event.results[i];
                    if (result.isFinal) {
                        finalTranscript += result[0].transcript;
                    } else {
                        interimTranscript += result[0].transcript;
                    }
                }

                const transcript = finalTranscript || interimTranscript;
                setState((prev) => ({ ...prev, transcript }));
                onResult?.(transcript, !!finalTranscript);
            };

            recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
                const errorMessage = getErrorMessage(event.error);
                setState((prev) => ({ ...prev, error: errorMessage, isListening: false }));
                onError?.(errorMessage);
            };
        }

        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, [language, continuous, interimResults, onResult, onError]);

    const startListening = useCallback(() => {
        if (recognitionRef.current && !state.isListening) {
            setState((prev) => ({ ...prev, transcript: "", error: null }));
            try {
                recognitionRef.current.start();
            } catch {
                // Already started
            }
        }
    }, [state.isListening]);

    const stopListening = useCallback(() => {
        if (recognitionRef.current && state.isListening) {
            recognitionRef.current.stop();
        }
    }, [state.isListening]);

    const toggleListening = useCallback(() => {
        if (state.isListening) {
            stopListening();
        } else {
            startListening();
        }
    }, [state.isListening, startListening, stopListening]);

    return {
        ...state,
        startListening,
        stopListening,
        toggleListening,
    };
}

function getErrorMessage(error: string): string {
    switch (error) {
        case "no-speech":
            return "No speech detected. Please try again.";
        case "audio-capture":
            return "No microphone found. Please check your microphone.";
        case "not-allowed":
            return "Microphone access denied. Please allow microphone access.";
        case "network":
            return "Network error. Please check your connection.";
        case "aborted":
            return "Voice input was cancelled.";
        case "language-not-supported":
            return "Language not supported.";
        default:
            return `Voice input error: ${error}`;
    }
}

// Language codes for voice recognition
export const voiceLanguages = {
    en: "en-US",
    ur: "ur-PK",
} as const;
