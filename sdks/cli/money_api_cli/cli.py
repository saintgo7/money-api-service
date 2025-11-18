"""Main CLI entry point."""
import click
import os
from pathlib import Path
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

from .client import MoneyAPIClient
from .config import Config

# Load environment variables
load_dotenv()

console = Console()
config = Config()


@click.group()
@click.version_option(version="2.0.0")
@click.option("--api-key", envvar="MONEY_API_KEY", help="API key for Money API")
@click.option("--base-url", envvar="MONEY_API_BASE_URL", default="https://api.money-api.com", help="Base API URL")
@click.pass_context
def cli(ctx, api_key, base_url):
    """Money API CLI - AI API platform with cost tracking and analytics."""
    ctx.ensure_object(dict)

    # Load API key from config if not provided
    if not api_key:
        api_key = config.get_api_key()

    if not api_key and ctx.invoked_subcommand not in ["configure", "init"]:
        console.print("[red]Error: API key not configured[/red]")
        console.print("Run: [cyan]money-api configure --api-key YOUR_KEY[/cyan]")
        ctx.exit(1)

    ctx.obj["client"] = MoneyAPIClient(api_key, base_url) if api_key else None
    ctx.obj["config"] = config


@cli.command()
@click.option("--api-key", required=True, help="Your Money API key")
@click.option("--base-url", default="https://api.money-api.com", help="Base API URL")
@click.pass_context
def configure(ctx, api_key, base_url):
    """Configure API credentials."""
    config = ctx.obj["config"]
    config.set_api_key(api_key)
    config.set_base_url(base_url)
    console.print("[green]✓ Configuration saved successfully[/green]")


@cli.command()
@click.argument("prompt")
@click.option("--model", default="claude-3-sonnet", help="Model name")
@click.option("--max-tokens", default=1000, help="Maximum tokens")
@click.option("--stream/--no-stream", default=False, help="Stream response")
@click.pass_context
def generate(ctx, prompt, model, max_tokens, stream):
    """Generate text completion."""
    client = ctx.obj["client"]

    try:
        if stream:
            console.print(f"[cyan]Generating with {model}...[/cyan]\n")
            for chunk in client.stream_text(prompt, model, max_tokens):
                console.print(chunk, end="")
            console.print("\n")
        else:
            with console.status(f"[cyan]Generating with {model}...[/cyan]"):
                result = client.generate_text(prompt, model, max_tokens)

            console.print(f"\n[green]{result['text']}[/green]\n")
            console.print(f"[dim]Model: {result['model']} | Cost: ${result['cost']:.4f} | Tokens: {result['usage']['total_tokens']}[/dim]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        ctx.exit(1)


@cli.command()
@click.argument("prompt")
@click.option("--model", default="sdxl", help="Model name")
@click.option("--width", default=1024, help="Image width")
@click.option("--height", default=1024, help="Image height")
@click.option("--output", "-o", help="Output file path")
@click.pass_context
def image(ctx, prompt, model, width, height, output):
    """Generate image."""
    client = ctx.obj["client"]

    try:
        with console.status(f"[cyan]Generating image with {model}...[/cyan]"):
            result = client.generate_image(prompt, model, width, height)

        console.print(f"\n[green]✓ Image generated successfully[/green]")
        console.print(f"URL: {result['url']}")
        console.print(f"[dim]Model: {result['model']} | Cost: ${result['cost']:.4f} | Size: {result['width']}x{result['height']}[/dim]")

        if output:
            import requests
            response = requests.get(result['url'])
            with open(output, 'wb') as f:
                f.write(response.content)
            console.print(f"[green]✓ Image saved to {output}[/green]")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        ctx.exit(1)


@cli.command()
@click.pass_context
def balance(ctx):
    """Get account balance."""
    client = ctx.obj["client"]

    try:
        result = client.get_balance()
        console.print(f"\n[green]Balance: ${result['balance']:.2f} {result['currency']}[/green]\n")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        ctx.exit(1)


@cli.command()
@click.option("--days", default=30, help="Number of days")
@click.pass_context
def usage(ctx, days):
    """Get usage statistics."""
    client = ctx.obj["client"]

    try:
        result = client.get_usage()

        table = Table(title="Usage Summary")
        table.add_column("Metric", style="cyan")
        table.add_column("Value", style="green")

        table.add_row("Total Requests", str(result['total_requests']))
        table.add_row("Total Cost", f"${result['total_cost']:.2f}")
        table.add_row("Period", result['period'])

        console.print("\n")
        console.print(table)
        console.print("\n")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        ctx.exit(1)


@cli.group()
def batch():
    """Batch processing commands."""
    pass


@batch.command("text")
@click.argument("file", type=click.File("r"))
@click.option("--model", default="claude-3-sonnet", help="Model name")
@click.option("--max-tokens", default=1000, help="Maximum tokens")
@click.option("--parallel/--sequential", default=True, help="Processing mode")
@click.pass_context
def batch_text(ctx, file, model, max_tokens, parallel):
    """Process batch text requests from file (one prompt per line)."""
    client = ctx.obj["client"]

    prompts = [line.strip() for line in file if line.strip()]

    if len(prompts) > 100:
        console.print("[red]Error: Maximum 100 prompts allowed[/red]")
        ctx.exit(1)

    requests = [
        {"prompt": prompt, "model": model, "max_tokens": max_tokens}
        for prompt in prompts
    ]

    try:
        with console.status(f"[cyan]Processing {len(requests)} requests...[/cyan]"):
            result = client.batch_text(requests, parallel)

        console.print(f"\n[green]✓ Batch processing completed[/green]")
        console.print(f"Successful: {result['successful']}/{result['total_requests']}")
        console.print(f"Failed: {result['failed']}")
        console.print(f"Total Cost: ${result['total_cost']:.4f}")
        console.print(f"Total Time: {result['total_time']:.2f}s\n")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        ctx.exit(1)


@cli.group()
def finetune():
    """Fine-tuning commands."""
    pass


@finetune.command("create")
@click.option("--training-file", required=True, help="Training file ID")
@click.option("--model", default="gpt-3.5-turbo", help="Base model")
@click.option("--suffix", help="Model name suffix")
@click.pass_context
def finetune_create(ctx, training_file, model, suffix):
    """Create fine-tuning job."""
    client = ctx.obj["client"]

    try:
        with console.status("[cyan]Creating fine-tuning job...[/cyan]"):
            result = client.create_finetune_job(training_file, model, suffix)

        console.print(f"\n[green]✓ Fine-tuning job created[/green]")
        console.print(f"Job ID: {result['id']}")
        console.print(f"Status: {result['status']}")
        console.print(f"Estimated Cost: ${result['estimated_cost']:.2f}\n")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        ctx.exit(1)


@finetune.command("list")
@click.option("--limit", default=20, help="Number of jobs to list")
@click.pass_context
def finetune_list(ctx, limit):
    """List fine-tuning jobs."""
    client = ctx.obj["client"]

    try:
        jobs = client.list_finetune_jobs(limit)

        table = Table(title="Fine-Tuning Jobs")
        table.add_column("Job ID", style="cyan")
        table.add_column("Status", style="green")
        table.add_column("Model", style="yellow")
        table.add_column("Progress", style="blue")

        for job in jobs:
            table.add_row(
                job['id'][:20] + "...",
                job['status'],
                job['model'],
                f"{job['progress_percentage']:.1f}%"
            )

        console.print("\n")
        console.print(table)
        console.print("\n")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        ctx.exit(1)


@finetune.command("status")
@click.argument("job_id")
@click.pass_context
def finetune_status(ctx, job_id):
    """Get fine-tuning job status."""
    client = ctx.obj["client"]

    try:
        job = client.get_finetune_job(job_id)

        console.print(f"\n[cyan]Job ID:[/cyan] {job['id']}")
        console.print(f"[cyan]Status:[/cyan] {job['status']}")
        console.print(f"[cyan]Model:[/cyan] {job['model']}")
        console.print(f"[cyan]Progress:[/cyan] {job['progress_percentage']:.1f}%")

        if job.get('fine_tuned_model'):
            console.print(f"[cyan]Fine-tuned Model:[/cyan] {job['fine_tuned_model']}")

        if job.get('training_loss'):
            console.print(f"[cyan]Training Loss:[/cyan] {job['training_loss']:.4f}")

        console.print(f"[cyan]Estimated Cost:[/cyan] ${job['estimated_cost']:.2f}")

        if job.get('actual_cost'):
            console.print(f"[cyan]Actual Cost:[/cyan] ${job['actual_cost']:.2f}")

        console.print("\n")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        ctx.exit(1)


@cli.group()
def ml():
    """Machine learning predictions."""
    pass


@ml.command("predict-cost")
@click.pass_context
def ml_predict_cost(ctx):
    """Predict next month's cost."""
    client = ctx.obj["client"]

    try:
        prediction = client.predict_cost()

        console.print(f"\n[cyan]Cost Prediction[/cyan]")
        console.print(f"Current Month: ${prediction['current_month']:.2f}")
        console.print(f"Predicted Next Month: ${prediction['predicted_next_month']:.2f}")
        console.print(f"Daily Average: ${prediction['predicted_daily_average']:.2f}")
        console.print(f"Trend: {prediction['trend']}")
        console.print(f"Confidence: {prediction['confidence'] * 100:.1f}%\n")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        ctx.exit(1)


@ml.command("detect-anomalies")
@click.option("--days", default=30, help="Number of days to analyze")
@click.pass_context
def ml_detect_anomalies(ctx, days):
    """Detect usage anomalies."""
    client = ctx.obj["client"]

    try:
        anomalies = client.detect_anomalies(days)

        if not anomalies:
            console.print("[green]No anomalies detected[/green]")
            return

        table = Table(title=f"Detected Anomalies (Last {days} days)")
        table.add_column("Date", style="cyan")
        table.add_column("Actual", style="yellow")
        table.add_column("Expected", style="green")
        table.add_column("Deviation", style="red")

        for anomaly in anomalies:
            table.add_row(
                anomaly['date'],
                f"${anomaly['actual_value']:.2f}",
                f"${anomaly['expected_value']:.2f}",
                f"{anomaly['deviation_percentage']:.1f}%"
            )

        console.print("\n")
        console.print(table)
        console.print("\n")
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        ctx.exit(1)


@ml.command("insights")
@click.pass_context
def ml_insights(ctx):
    """Get usage insights and recommendations."""
    client = ctx.obj["client"]

    try:
        insights = client.get_insights()

        console.print(f"\n[cyan]Usage Insights[/cyan]\n")

        if insights.get('recommendations'):
            console.print("[yellow]Recommendations:[/yellow]")
            for rec in insights['recommendations']:
                priority_color = {
                    'high': 'red',
                    'medium': 'yellow',
                    'low': 'green'
                }.get(rec['priority'], 'white')
                console.print(f"  [{priority_color}][{rec['priority'].upper()}][/{priority_color}] {rec['message']}")
            console.print()

        if insights.get('cost_breakdown'):
            table = Table(title="Cost Breakdown")
            table.add_column("Endpoint", style="cyan")
            table.add_column("Requests", style="green")
            table.add_column("Cost", style="yellow")
            table.add_column("Percentage", style="blue")

            for item in insights['cost_breakdown'][:10]:
                table.add_row(
                    item['endpoint'],
                    str(item['requests']),
                    f"${item['cost']:.2f}",
                    f"{item['percentage']:.1f}%"
                )

            console.print(table)
            console.print()
    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/red]")
        ctx.exit(1)


if __name__ == "__main__":
    cli()
