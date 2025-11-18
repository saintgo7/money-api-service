"""Content generator for marketing copy."""
from money_api import MoneyAPI
import json


def generate_marketing_content(
    client: MoneyAPI,
    product_name: str,
    product_description: str,
    target_audience: str
) -> dict:
    """Generate marketing content for a product.

    Args:
        client: Money API client
        product_name: Product name
        product_description: Product description
        target_audience: Target audience

    Returns:
        Dictionary with generated content
    """
    results = {}

    # 1. Generate headline
    print("📝 Generating headline...")
    headline_prompt = f"""
    Create a compelling marketing headline for this product:
    Product: {product_name}
    Description: {product_description}
    Target Audience: {target_audience}

    Generate 3 catchy headlines (one per line):
    """

    response = client.text.complete(
        prompt=headline_prompt,
        max_tokens=200,
        temperature=0.9
    )
    results['headlines'] = response['content'].strip().split('\n')
    results['headline_cost'] = response['cost']

    # 2. Generate product description
    print("📝 Generating product description...")
    description_prompt = f"""
    Write a compelling 2-paragraph product description for:
    Product: {product_name}
    Features: {product_description}
    Target Audience: {target_audience}

    Make it engaging and highlight benefits.
    """

    response = client.text.complete(
        prompt=description_prompt,
        max_tokens=400,
        temperature=0.7
    )
    results['description'] = response['content'].strip()
    results['description_cost'] = response['cost']

    # 3. Generate social media posts
    print("📝 Generating social media posts...")
    social_prompt = f"""
    Create 3 social media posts (Twitter/X format, under 280 characters) for:
    Product: {product_name}
    Description: {product_description}

    Make them catchy and include relevant hashtags.
    """

    response = client.text.complete(
        prompt=social_prompt,
        max_tokens=300,
        temperature=0.8
    )
    results['social_posts'] = response['content'].strip().split('\n\n')
    results['social_cost'] = response['cost']

    # 4. Generate email subject lines
    print("📝 Generating email subject lines...")
    email_prompt = f"""
    Create 5 compelling email subject lines to promote:
    Product: {product_name}
    Target: {target_audience}

    Make them attention-grabbing but not spammy.
    """

    response = client.text.complete(
        prompt=email_prompt,
        max_tokens=200,
        temperature=0.8
    )
    results['email_subjects'] = response['content'].strip().split('\n')
    results['email_cost'] = response['cost']

    # Calculate total cost
    results['total_cost'] = (
        results['headline_cost'] +
        results['description_cost'] +
        results['social_cost'] +
        results['email_cost']
    )

    return results


def main():
    """Run content generator."""
    print("🎨 Money API Content Generator\n")

    # Get inputs
    api_key = input("Enter your Money API key: ").strip()
    product_name = input("Product name: ").strip()
    product_description = input("Product description: ").strip()
    target_audience = input("Target audience: ").strip()

    if not all([api_key, product_name, product_description, target_audience]):
        print("❌ All fields are required")
        return

    # Initialize client
    client = MoneyAPI(api_key=api_key)

    print("\n🚀 Generating content...\n")

    try:
        # Generate content
        results = generate_marketing_content(
            client,
            product_name,
            product_description,
            target_audience
        )

        # Display results
        print("\n" + "="*60)
        print("📊 MARKETING CONTENT PACKAGE")
        print("="*60)

        print("\n📢 HEADLINES:")
        for i, headline in enumerate(results['headlines'][:3], 1):
            print(f"  {i}. {headline.strip()}")

        print("\n📝 PRODUCT DESCRIPTION:")
        print(f"  {results['description']}")

        print("\n💬 SOCIAL MEDIA POSTS:")
        for i, post in enumerate(results['social_posts'][:3], 1):
            print(f"\n  Post {i}:")
            print(f"  {post.strip()}")

        print("\n📧 EMAIL SUBJECT LINES:")
        for i, subject in enumerate(results['email_subjects'][:5], 1):
            print(f"  {i}. {subject.strip()}")

        print("\n" + "="*60)
        print(f"💰 Total Cost: ${results['total_cost']:.4f}")
        print("="*60)

        # Save to file
        output_file = f"{product_name.lower().replace(' ', '_')}_marketing.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\n💾 Results saved to: {output_file}")

    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()
