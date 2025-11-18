"""Batch image generation example."""
import sys
import json
import base64
from pathlib import Path
from money_api import MoneyAPI


def generate_images_from_prompts(
    client: MoneyAPI,
    prompts_file: str,
    output_dir: str,
    model: str = "sdxl",
    size: str = "1024x1024"
):
    """Generate images from a list of prompts.

    Args:
        client: Money API client
        prompts_file: JSON file with prompts
        output_dir: Directory to save images
        model: Model to use
        size: Image size
    """
    # Read prompts
    with open(prompts_file, 'r') as f:
        data = json.load(f)

    prompts = data.get('prompts', [])

    if not prompts:
        print("❌ No prompts found in file")
        return

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"🎨 Generating {len(prompts)} images...")
    print(f"📁 Output directory: {output_dir}\n")

    total_cost = 0.0
    results = []

    for i, prompt in enumerate(prompts, 1):
        print(f"[{i}/{len(prompts)}] Generating: {prompt[:50]}...")

        try:
            # Generate image
            response = client.image.generate(
                prompt=prompt,
                model=model,
                size=size,
                n=1
            )

            image_url = response['images'][0]
            cost = response['cost']
            total_cost += cost

            # Save result
            results.append({
                'prompt': prompt,
                'image_url': image_url,
                'cost': cost,
                'status': 'success'
            })

            print(f"  ✅ Generated (${cost:.4f})")

        except Exception as e:
            print(f"  ❌ Error: {e}")
            results.append({
                'prompt': prompt,
                'error': str(e),
                'status': 'failed'
            })

    # Save results
    results_file = output_path / 'results.json'
    with open(results_file, 'w') as f:
        json.dump({
            'total_images': len(prompts),
            'successful': sum(1 for r in results if r['status'] == 'success'),
            'failed': sum(1 for r in results if r['status'] == 'failed'),
            'total_cost': total_cost,
            'results': results
        }, f, indent=2)

    print(f"\n✨ Generation complete!")
    print(f"📊 Success: {sum(1 for r in results if r['status'] == 'success')}/{len(prompts)}")
    print(f"💰 Total cost: ${total_cost:.2f}")
    print(f"💾 Results saved to: {results_file}")


def main():
    """Run batch image generator."""
    if len(sys.argv) < 4:
        print("Usage: python image_batch_generator.py <api_key> <prompts.json> <output_dir>")
        print("\nPrompts file format:")
        print(json.dumps({
            "prompts": [
                "A sunset over mountains",
                "A futuristic city",
                "A peaceful forest"
            ]
        }, indent=2))
        sys.exit(1)

    api_key = sys.argv[1]
    prompts_file = sys.argv[2]
    output_dir = sys.argv[3]

    # Validate prompts file
    if not Path(prompts_file).exists():
        print(f"❌ Prompts file not found: {prompts_file}")
        sys.exit(1)

    # Initialize client
    client = MoneyAPI(api_key=api_key)

    # Generate images
    generate_images_from_prompts(client, prompts_file, output_dir)


if __name__ == "__main__":
    main()
