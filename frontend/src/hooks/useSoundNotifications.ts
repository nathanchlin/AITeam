import { useCallback, useRef, useEffect } from 'react';

type SoundType = 'success' | 'error' | 'notification' | 'warning';

// Sound URLs using Web Audio API generated tones
const TONES: Record<SoundType, { frequency: number; duration: number; type: OscillatorType; gain: number }> = {
  success: { frequency: 880, duration: 0.15, type: 'sine', gain: 0.3 },  // A5 - pleasant chime
  error: { frequency: 220, duration: 0.3, type: 'square', gain: 0.2 },   // A3 - alert tone
  notification: { frequency: 660, duration: 0.1, type: 'sine', gain: 0.25 }, // E5 - quick ping
  warning: { frequency: 440, duration: 0.2, type: 'triangle', gain: 0.25 }, // A4 - attention
};

interface UseSoundNotificationsOptions {
  enabled?: boolean;
  volume?: number; // 0-1
}

// Storage key for preference
const SOUND_ENABLED_KEY = 'aiteam_sound_notifications';
const SOUND_VOLUME_KEY = 'aiteam_sound_volume';

export function useSoundNotifications(options: UseSoundNotificationsOptions = {}) {
  const { enabled: initialEnabled = true, volume: initialVolume = 0.5 } = options;

  // Get stored preference
  const getStoredEnabled = (): boolean => {
    try {
      const stored = localStorage.getItem(SOUND_ENABLED_KEY);
      return stored ? JSON.parse(stored) : initialEnabled;
    } catch {
      return initialEnabled;
    }
  };

  // Get stored volume
  const getStoredVolume = (): number => {
    try {
      const stored = localStorage.getItem(SOUND_VOLUME_KEY);
      return stored ? JSON.parse(stored) : initialVolume;
    } catch {
      return initialVolume;
    }
  };

  const [enabledState, setEnabledState] = [getStoredEnabled(), useCallback((value: boolean) => {
    localStorage.setItem(SOUND_ENABLED_KEY, JSON.stringify(value));
  }, [])];

  // Suppress unused variable warning - used by toggleEnabled
  void enabledState;

  const volume = useRef(getStoredVolume());
  const audioContextRef = useRef<AudioContext | null>(null);

  // Initialize AudioContext on first user interaction
  const initAudioContext = useCallback(() => {
    if (!audioContextRef.current) {
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)();
    }
    return audioContextRef.current;
  }, []);

  // Play a tone using Web Audio API
  const playSound = useCallback((type: SoundType) => {
    if (!getStoredEnabled()) return;

    try {
      const ctx = initAudioContext();
      const tone = TONES[type];

      const oscillator = ctx.createOscillator();
      const gainNode = ctx.createGain();

      oscillator.connect(gainNode);
      gainNode.connect(ctx.destination);

      oscillator.type = tone.type;
      oscillator.frequency.setValueAtTime(tone.frequency, ctx.currentTime);

      gainNode.gain.setValueAtTime(tone.gain * volume.current, ctx.currentTime);
      gainNode.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + tone.duration);

      oscillator.start(ctx.currentTime);
      oscillator.stop(ctx.currentTime + tone.duration);

      // Play second chime for success (two-tone effect)
      if (type === 'success') {
        setTimeout(() => {
          const osc2 = ctx.createOscillator();
          const gain2 = ctx.createGain();
          osc2.connect(gain2);
          gain2.connect(ctx.destination);
          osc2.type = 'sine';
          osc2.frequency.setValueAtTime(1108.73, ctx.currentTime); // C#6
          gain2.gain.setValueAtTime(tone.gain * volume.current * 0.7, ctx.currentTime);
          gain2.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.1);
          osc2.start(ctx.currentTime);
          osc2.stop(ctx.currentTime + 0.1);
        }, 150);
      }
    } catch (e) {
      console.warn('[Sound] Failed to play sound:', e);
    }
  }, [initAudioContext]);

  // Toggle sound notifications
  const toggleEnabled = useCallback(() => {
    const newValue = !getStoredEnabled();
    localStorage.setItem(SOUND_ENABLED_KEY, JSON.stringify(newValue));
    setEnabledState(newValue);
    // Play test sound when enabling
    if (newValue) {
      playSound('notification');
    }
    return newValue;
  }, [playSound, setEnabledState]);

  // Set volume
  const setVolume = useCallback((newVolume: number) => {
    const clamped = Math.max(0, Math.min(1, newVolume));
    volume.current = clamped;
    localStorage.setItem(SOUND_VOLUME_KEY, JSON.stringify(clamped));
  }, []);

  // Get current volume (for UI binding)
  const getVolume = useCallback(() => volume.current, []);

  // Initialize on mount (needs user interaction to actually work)
  useEffect(() => {
    // Pre-initialize on first click anywhere
    const handleFirstInteraction = () => {
      initAudioContext();
      document.removeEventListener('click', handleFirstInteraction);
    };
    document.addEventListener('click', handleFirstInteraction);
    return () => document.removeEventListener('click', handleFirstInteraction);
  }, [initAudioContext]);

  return {
    playSound,
    enabled: getStoredEnabled(),
    toggleEnabled,
    setVolume,
    getVolume,
    volume: volume.current,
  };
}

// Play sound for specific events
export function useTaskSoundNotifications() {
  const { playSound, enabled } = useSoundNotifications();

  const playTaskComplete = useCallback(() => {
    playSound('success');
  }, [playSound]);

  const playTaskError = useCallback(() => {
    playSound('error');
  }, [playSound]);

  const playTaskStart = useCallback(() => {
    playSound('notification');
  }, [playSound]);

  return {
    playTaskComplete,
    playTaskError,
    playTaskStart,
    soundEnabled: enabled,
  };
}
