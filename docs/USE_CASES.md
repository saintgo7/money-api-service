# Use Cases & Examples

Real-world applications built with Money API Service.

## 🤖 AI Chatbots

### Customer Support Bot

```python
from money_api import MoneyAPI

client = MoneyAPI(api_key="sk_...")

# Context-aware support bot
conversation_history = []

def answer_question(question: str) -> str:
    # Build context from history
    context = "\n".join(conversation_history[-5:])

    response = client.text.complete(
        prompt=question,
        system=f"""You are a helpful customer support agent.
        Previous conversation:
        {context}

        Answer the customer's question professionally and helpfully.""",
        max_tokens=500
    )

    # Update history
    conversation_history.append(f"Customer: {question}")
    conversation_history.append(f"Agent: {response['content']}")

    return response['content']
```

**Use in**: E-commerce, SaaS products, Help desks

**Cost**: ~$0.01-0.05 per conversation

---

## 📝 Content Generation

### Blog Post Writer

```python
def generate_blog_post(topic: str, keywords: list) -> dict:
    # Generate outline
    outline_response = client.text.complete(
        prompt=f"""Create a detailed outline for a blog post about {topic}.
        Include: introduction, 3-5 main sections, and conclusion.
        Target keywords: {', '.join(keywords)}""",
        max_tokens=500
    )

    # Generate full post
    post_response = client.text.complete(
        prompt=f"""Write a complete blog post based on this outline:
        {outline_response['content']}

        Make it engaging, informative, and SEO-optimized.
        Target length: 1500 words.""",
        max_tokens=2000
    )

    # Generate meta description
    meta_response = client.text.complete(
        prompt=f"Write a compelling 155-character meta description for:\n{post_response['content']}",
        max_tokens=50
    )

    return {
        "title": topic,
        "content": post_response['content'],
        "meta_description": meta_response['content'],
        "total_cost": (
            outline_response['cost'] +
            post_response['cost'] +
            meta_response['cost']
        )
    }
```

**Use in**: Marketing agencies, Content platforms, SEO tools

**Cost**: ~$0.05-0.15 per blog post

---

## 🌍 Translation Services

### Multi-Language Content Platform

```python
class TranslationService:
    def __init__(self, api_key: str):
        self.client = MoneyAPI(api_key=api_key)
        self.cache = {}  # Simple cache

    def translate_bulk(self, texts: list, target_langs: list) -> dict:
        """Translate multiple texts to multiple languages."""
        results = {}

        for lang in target_langs:
            results[lang] = []

            for text in texts:
                # Check cache
                cache_key = f"{text}:{lang}"
                if cache_key in self.cache:
                    results[lang].append(self.cache[cache_key])
                    continue

                # Translate
                response = self.client.text.translate(
                    text=text,
                    source_lang="en",
                    target_lang=lang
                )

                translation = response['translated_text']
                results[lang].append(translation)

                # Cache result
                self.cache[cache_key] = translation

        return results
```

**Use in**: E-commerce, Apps, Documentation platforms

**Cost**: ~$0.005 per 1K characters

---

## 🎨 Image Generation

### Product Mockup Generator

```python
def generate_product_mockups(product_name: str, variations: list) -> list:
    """Generate product images in different styles."""
    mockups = []

    styles = [
        "professional studio lighting, white background",
        "lifestyle photo, natural setting",
        "minimalist, clean aesthetic",
        "editorial style, dramatic lighting"
    ]

    for i, style in enumerate(styles):
        prompt = f"""{product_name}, {style},
        high quality, 4K, product photography"""

        response = client.image.generate(
            prompt=prompt,
            model="sdxl",
            size="1024x1024"
        )

        mockups.append({
            "style": variations[i] if i < len(variations) else f"Style {i+1}",
            "image_url": response['images'][0],
            "cost": response['cost']
        })

    return mockups
```

**Use in**: E-commerce, Marketing, Design tools

**Cost**: ~$0.02-0.04 per image

---

## 🎤 Voice Applications

### Podcast Transcription Service

```python
import asyncio

async def transcribe_podcast(audio_file_path: str) -> dict:
    """Transcribe podcast with timestamps."""
    with open(audio_file_path, 'rb') as f:
        audio_data = f.read()

    # Transcribe
    response = await client.audio.transcribe(
        audio=audio_data,
        timestamps=True
    )

    # Generate summary
    summary_response = await client.text.summarize(
        text=response['text'],
        length="medium"
    )

    # Extract key points
    points_response = await client.text.complete(
        prompt=f"""Extract 5-7 key points from this podcast transcript:
        {response['text']}

        Format as bullet points.""",
        max_tokens=300
    )

    return {
        "transcript": response['text'],
        "duration": response['duration'],
        "summary": summary_response['summary'],
        "key_points": points_response['content'],
        "total_cost": (
            response['cost'] +
            summary_response['cost'] +
            points_response['cost']
        )
    }
```

**Use in**: Podcast platforms, Media companies, Content creators

**Cost**: ~$0.006-0.02 per minute of audio

---

## 📄 Document Processing

### Contract Analysis System

```python
def analyze_contract(pdf_path: str) -> dict:
    """Analyze legal contract and extract key information."""
    with open(pdf_path, 'rb') as f:
        doc_data = f.read()

    # Parse document
    parsed = client.document.parse(
        document=doc_data,
        extract_tables=True
    )

    # Q&A about contract
    questions = [
        "What are the key terms and conditions?",
        "What is the contract duration?",
        "What are the payment terms?",
        "What are the termination clauses?",
        "Are there any unusual or risky provisions?"
    ]

    qa_response = client.document.qa(
        document=doc_data,
        questions=questions
    )

    # Generate summary
    summary_response = client.text.summarize(
        text=parsed['text'],
        length="medium"
    )

    return {
        "summary": summary_response['summary'],
        "qa": qa_response['answers'],
        "page_count": parsed['page_count'],
        "tables": parsed['tables']
    }
```

**Use in**: Legal tech, HR platforms, Real estate

**Cost**: ~$0.01-0.05 per document

---

## 💬 Sentiment Analysis

### Social Media Monitor

```python
class SocialMediaMonitor:
    def __init__(self, api_key: str):
        self.client = MoneyAPI(api_key=api_key)

    def analyze_mentions(self, mentions: list) -> dict:
        """Analyze sentiment of brand mentions."""
        results = {
            "positive": [],
            "negative": [],
            "neutral": [],
            "total_sentiment_score": 0
        }

        for mention in mentions:
            sentiment = self.client.text.analyzeSentiment(mention['text'])

            mention_data = {
                **mention,
                "sentiment": sentiment['sentiment'],
                "score": sentiment['score']
            }

            results[sentiment['sentiment']].append(mention_data)
            results['total_sentiment_score'] += sentiment['score']

        results['average_sentiment'] = (
            results['total_sentiment_score'] / len(mentions)
            if mentions else 0
        )

        return results
```

**Use in**: Marketing tools, Brand monitoring, Customer feedback

**Cost**: ~$0.001 per mention

---

## 🎯 Smart Email Marketing

### Personalized Email Generator

```python
def generate_personalized_email(customer: dict, product: str) -> str:
    """Generate personalized marketing email."""
    # Analyze customer interests
    interests = ", ".join(customer.get('interests', []))
    purchase_history = customer.get('previous_purchases', [])

    response = client.text.complete(
        prompt=f"""Write a personalized marketing email for {customer['name']}.

        Customer info:
        - Interests: {interests}
        - Previous purchases: {purchase_history}
        - Preferred tone: {customer.get('communication_preference', 'friendly')}

        Product to promote: {product}

        Make it personal, engaging, and include a clear call-to-action.
        Keep it under 200 words.""",
        max_tokens=400
    )

    return response['content']
```

**Use in**: Email marketing platforms, CRM systems, E-commerce

**Cost**: ~$0.001-0.003 per email

---

## 💡 Code Generation

### API Documentation Generator

```python
def generate_api_docs(code: str, language: str) -> dict:
    """Generate API documentation from code."""
    # Generate docstrings
    docs_response = client.text.complete(
        prompt=f"""Analyze this {language} code and generate comprehensive API documentation:

        ```{language}
        {code}
        ```

        Include:
        - Function/method descriptions
        - Parameters with types
        - Return values
        - Usage examples
        - Edge cases""",
        max_tokens=1500
    )

    # Generate examples
    examples_response = client.text.complete(
        prompt=f"""Create 3 practical code examples showing how to use this API:

        {code}

        Show different use cases.""",
        max_tokens=800
    )

    return {
        "documentation": docs_response['content'],
        "examples": examples_response['content']
    }
```

**Use in**: Developer tools, Documentation platforms, Code editors

**Cost**: ~$0.01-0.03 per documentation set

---

## 📊 Business Intelligence

### Automated Report Generator

```python
def generate_business_report(data: dict) -> str:
    """Generate executive summary from business data."""
    response = client.text.complete(
        prompt=f"""Create an executive business report based on this data:

        Revenue: ${data['revenue']:,.2f}
        Growth: {data['growth_rate']}%
        Customer Acquisition Cost: ${data['cac']}
        Lifetime Value: ${data['ltv']}
        Active Users: {data['active_users']:,}
        Churn Rate: {data['churn_rate']}%

        Provide:
        1. Key insights and trends
        2. Performance highlights
        3. Areas of concern
        4. Recommendations

        Make it concise and actionable for executives.""",
        max_tokens=1000
    )

    return response['content']
```

**Use in**: Analytics platforms, BI tools, Dashboards

**Cost**: ~$0.003-0.01 per report

---

## 🎓 Education

### Adaptive Learning System

```python
def create_personalized_lesson(
    topic: str,
    student_level: str,
    learning_style: str
) -> dict:
    """Create personalized educational content."""
    # Generate lesson
    lesson_response = client.text.complete(
        prompt=f"""Create a {student_level}-level lesson about {topic}.

        Learning style: {learning_style}

        Include:
        - Clear explanation
        - Real-world examples
        - Interactive exercises
        - Key takeaways

        Make it engaging and appropriate for the student's level.""",
        max_tokens=1500
    )

    # Generate quiz
    quiz_response = client.text.complete(
        prompt=f"""Create 5 multiple-choice questions to test understanding of:
        {lesson_response['content']}

        Format: Question, 4 options (A-D), correct answer.""",
        max_tokens=500
    )

    return {
        "lesson": lesson_response['content'],
        "quiz": quiz_response['content']
    }
```

**Use in**: EdTech platforms, Online courses, Tutoring apps

**Cost**: ~$0.01-0.05 per lesson

---

## 🔍 SEO Optimization

### SEO Content Optimizer

```python
def optimize_for_seo(content: str, target_keyword: str) -> dict:
    """Optimize content for SEO."""
    # Analyze current content
    analysis_response = client.text.complete(
        prompt=f"""Analyze this content for SEO optimization for keyword "{target_keyword}":

        {content}

        Provide specific recommendations for:
        - Keyword density
        - Header structure (H1, H2, H3)
        - Meta tags
        - Internal linking opportunities
        - Content gaps""",
        max_tokens=800
    )

    # Generate optimized version
    optimized_response = client.text.complete(
        prompt=f"""Rewrite this content optimized for SEO keyword "{target_keyword}":

        {content}

        Maintain the original meaning but improve:
        - Keyword placement
        - Readability
        - Structure
        - Engagement""",
        max_tokens=2000
    )

    return {
        "analysis": analysis_response['content'],
        "optimized_content": optimized_response['content']
    }
```

**Use in**: SEO tools, Content platforms, Marketing agencies

**Cost**: ~$0.01-0.05 per optimization

---

## Cost Optimization Tips

1. **Cache frequently requested content**
2. **Use appropriate max_tokens limits**
3. **Batch similar requests together**
4. **Choose the right model** (Claude Sonnet vs GPT-4)
5. **Implement request deduplication**
6. **Monitor usage with webhooks**

## Getting Started

All examples are available in the [examples/](../examples/) directory.

Choose your use case and start building! 🚀
