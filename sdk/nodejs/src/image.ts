import { AxiosInstance } from 'axios';

export interface ImageGenerateRequest {
  prompt: string;
  model?: string;
  size?: string;
  n?: number;
  style?: string;
}

export interface ImageResponse {
  images: string[];
  prompt: string;
  model: string;
  cost: number;
}

export class ImageAPI {
  constructor(private client: AxiosInstance) {}

  /**
   * Generate images from text
   */
  async generate(request: ImageGenerateRequest): Promise<ImageResponse> {
    const response = await this.client.post('/api/v1/image/generate', {
      prompt: request.prompt,
      model: request.model || 'sdxl',
      size: request.size || '1024x1024',
      n: request.n || 1,
      style: request.style
    });
    return response.data;
  }

  /**
   * Edit image with inpainting
   */
  async edit(image: Buffer, mask: Buffer | null, prompt: string): Promise<any> {
    const FormData = require('form-data');
    const formData = new FormData();

    formData.append('image', image, 'image.png');
    if (mask) {
      formData.append('mask', mask, 'mask.png');
    }
    formData.append('prompt', prompt);

    const response = await this.client.post('/api/v1/image/edit', formData, {
      headers: formData.getHeaders()
    });
    return response.data;
  }

  /**
   * Upscale image
   */
  async upscale(image: Buffer, scale: number = 4): Promise<any> {
    const FormData = require('form-data');
    const formData = new FormData();

    formData.append('image', image, 'image.png');
    formData.append('scale', scale.toString());

    const response = await this.client.post('/api/v1/image/upscale', formData, {
      headers: formData.getHeaders()
    });
    return response.data;
  }

  /**
   * Remove background from image
   */
  async removeBackground(image: Buffer): Promise<any> {
    const FormData = require('form-data');
    const formData = new FormData();

    formData.append('image', image, 'image.png');

    const response = await this.client.post('/api/v1/image/remove-background', formData, {
      headers: formData.getHeaders()
    });
    return response.data;
  }

  /**
   * Describe image content
   */
  async describe(image: Buffer): Promise<any> {
    const FormData = require('form-data');
    const formData = new FormData();

    formData.append('image', image, 'image.png');

    const response = await this.client.post('/api/v1/image/describe', formData, {
      headers: formData.getHeaders()
    });
    return response.data;
  }

  /**
   * Extract text from image (OCR)
   */
  async extractText(image: Buffer, language: string = 'auto'): Promise<any> {
    const FormData = require('form-data');
    const formData = new FormData();

    formData.append('image', image, 'image.png');
    formData.append('language', language);

    const response = await this.client.post('/api/v1/image/ocr', formData, {
      headers: formData.getHeaders()
    });
    return response.data;
  }
}
