import { AxiosInstance } from 'axios';

export interface ParsedDocument {
  text: string;
  tables?: any[];
  images?: string[];
  metadata: Record<string, any>;
  page_count: number;
}

export class DocumentAPI {
  constructor(private client: AxiosInstance) {}

  /**
   * Parse document (PDF, DOCX, etc.)
   */
  async parse(
    document: Buffer,
    extractTables: boolean = true,
    extractImages: boolean = false
  ): Promise<ParsedDocument> {
    const FormData = require('form-data');
    const formData = new FormData();

    formData.append('document', document, 'document.pdf');
    formData.append('extract_tables', extractTables.toString());
    formData.append('extract_images', extractImages.toString());

    const response = await this.client.post('/api/v1/document/parse', formData, {
      headers: formData.getHeaders()
    });
    return response.data;
  }

  /**
   * Ask questions about document
   */
  async qa(document: Buffer, questions: string[]): Promise<any> {
    const FormData = require('form-data');
    const formData = new FormData();

    formData.append('document', document, 'document.pdf');
    formData.append('questions', JSON.stringify(questions));

    const response = await this.client.post('/api/v1/document/qa', formData, {
      headers: formData.getHeaders()
    });
    return response.data;
  }

  /**
   * Summarize document
   */
  async summarize(document: Buffer, length: string = 'medium'): Promise<any> {
    const FormData = require('form-data');
    const formData = new FormData();

    formData.append('document', document, 'document.pdf');
    formData.append('length', length);

    const response = await this.client.post('/api/v1/document/summarize', formData, {
      headers: formData.getHeaders()
    });
    return response.data;
  }
}
