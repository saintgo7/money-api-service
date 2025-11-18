import { AxiosInstance } from 'axios';

export interface SynthesizeRequest {
  text: string;
  voice?: string;
  speed?: number;
  format?: string;
}

export interface TranscribeResponse {
  text: string;
  language: string;
  duration: number;
  cost: number;
  timestamps?: any[];
}

export class AudioAPI {
  constructor(private client: AxiosInstance) {}

  /**
   * Transcribe audio to text
   */
  async transcribe(
    audio: Buffer,
    language: string = 'auto',
    timestamps: boolean = false
  ): Promise<TranscribeResponse> {
    const FormData = require('form-data');
    const formData = new FormData();

    formData.append('audio', audio, 'audio.mp3');
    formData.append('language', language);
    formData.append('timestamps', timestamps.toString());

    const response = await this.client.post('/api/v1/audio/transcribe', formData, {
      headers: formData.getHeaders()
    });
    return response.data;
  }

  /**
   * Convert text to speech
   */
  async synthesize(request: SynthesizeRequest): Promise<any> {
    const response = await this.client.post('/api/v1/audio/synthesize', {
      text: request.text,
      voice: request.voice || 'alloy',
      speed: request.speed || 1.0,
      format: request.format || 'mp3'
    });
    return response.data;
  }

  /**
   * Clone voice from reference audio
   */
  async cloneVoice(referenceAudio: Buffer, text: string): Promise<any> {
    const FormData = require('form-data');
    const formData = new FormData();

    formData.append('reference_audio', referenceAudio, 'reference.mp3');
    formData.append('text', text);

    const response = await this.client.post('/api/v1/audio/clone-voice', formData, {
      headers: formData.getHeaders()
    });
    return response.data;
  }
}
