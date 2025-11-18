import * as vscode from 'vscode';
import { MoneyAPIClient } from './client';
import { AccountExplorerProvider } from './providers/accountExplorerProvider';
import { InsightsProvider } from './providers/insightsProvider';

let client: MoneyAPIClient;
let accountExplorerProvider: AccountExplorerProvider;
let insightsProvider: InsightsProvider;
let autoRefreshTimer: NodeJS.Timeout | undefined;

export function activate(context: vscode.ExtensionContext) {
    console.log('Money API extension is now active!');

    // Initialize client
    const apiKey = vscode.workspace.getConfiguration('moneyApi').get<string>('apiKey');
    const baseUrl = vscode.workspace.getConfiguration('moneyApi').get<string>('baseUrl') || 'https://api.money-api.com';

    if (apiKey) {
        client = new MoneyAPIClient(apiKey, baseUrl);
    }

    // Register providers
    accountExplorerProvider = new AccountExplorerProvider(client);
    insightsProvider = new InsightsProvider(client);

    vscode.window.registerTreeDataProvider('moneyApiExplorer', accountExplorerProvider);
    vscode.window.registerTreeDataProvider('moneyApiInsights', insightsProvider);

    // Register commands
    const commands = [
        vscode.commands.registerCommand('money-api.configure', configureApiKey),
        vscode.commands.registerCommand('money-api.generate', generateText),
        vscode.commands.registerCommand('money-api.generateImage', generateImage),
        vscode.commands.registerCommand('money-api.showBalance', showBalance),
        vscode.commands.registerCommand('money-api.showUsage', showUsage),
        vscode.commands.registerCommand('money-api.predictCost', predictCost),
        vscode.commands.registerCommand('money-api.detectAnomalies', detectAnomalies),
        vscode.commands.registerCommand('money-api.refresh', refresh)
    ];

    commands.forEach(cmd => context.subscriptions.push(cmd));

    // Setup auto-refresh
    setupAutoRefresh();

    // Watch configuration changes
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration(e => {
            if (e.affectsConfiguration('moneyApi')) {
                reinitializeClient();
                setupAutoRefresh();
            }
        })
    );
}

export function deactivate() {
    if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
    }
}

function reinitializeClient() {
    const apiKey = vscode.workspace.getConfiguration('moneyApi').get<string>('apiKey');
    const baseUrl = vscode.workspace.getConfiguration('moneyApi').get<string>('baseUrl') || 'https://api.money-api.com';

    if (apiKey) {
        client = new MoneyAPIClient(apiKey, baseUrl);
        accountExplorerProvider.updateClient(client);
        insightsProvider.updateClient(client);
    }
}

function setupAutoRefresh() {
    if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
    }

    const interval = vscode.workspace.getConfiguration('moneyApi').get<number>('autoRefreshInterval') || 0;

    if (interval > 0) {
        autoRefreshTimer = setInterval(() => {
            refresh();
        }, interval * 1000);
    }
}

async function configureApiKey() {
    const apiKey = await vscode.window.showInputBox({
        prompt: 'Enter your Money API key',
        password: true,
        ignoreFocusOut: true
    });

    if (apiKey) {
        await vscode.workspace.getConfiguration('moneyApi').update('apiKey', apiKey, vscode.ConfigurationTarget.Global);
        vscode.window.showInformationMessage('✓ API key configured successfully');
        reinitializeClient();
        refresh();
    }
}

async function generateText() {
    if (!ensureClientInitialized()) return;

    const editor = vscode.window.activeTextEditor;
    let prompt: string | undefined;

    // Use selection if available
    if (editor && !editor.selection.isEmpty) {
        prompt = editor.document.getText(editor.selection);
    } else {
        prompt = await vscode.window.showInputBox({
            prompt: 'Enter prompt for text generation',
            placeHolder: 'Explain quantum computing...'
        });
    }

    if (!prompt) return;

    const model = vscode.workspace.getConfiguration('moneyApi').get<string>('defaultModel') || 'claude-3-sonnet';
    const maxTokens = vscode.workspace.getConfiguration('moneyApi').get<number>('maxTokens') || 1000;

    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: `Generating with ${model}...`,
            cancellable: false
        }, async () => {
            const result = await client.generateText(prompt!, model, maxTokens);

            // Insert result
            if (editor) {
                await editor.edit(editBuilder => {
                    if (!editor.selection.isEmpty) {
                        editBuilder.replace(editor.selection, result.text);
                    } else {
                        editBuilder.insert(editor.selection.active, result.text);
                    }
                });
            } else {
                // Show in new document
                const doc = await vscode.workspace.openTextDocument({
                    content: result.text,
                    language: 'markdown'
                });
                await vscode.window.showTextDocument(doc);
            }

            // Show cost notification
            if (vscode.workspace.getConfiguration('moneyApi').get<boolean>('showCostNotifications')) {
                vscode.window.showInformationMessage(
                    `✓ Generated | Cost: $${result.cost.toFixed(4)} | Tokens: ${result.usage.total_tokens}`
                );
            }

            refresh();
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function generateImage() {
    if (!ensureClientInitialized()) return;

    const prompt = await vscode.window.showInputBox({
        prompt: 'Enter prompt for image generation',
        placeHolder: 'A serene mountain landscape at sunset...'
    });

    if (!prompt) return;

    const model = 'sdxl';
    const width = 1024;
    const height = 1024;

    try {
        await vscode.window.withProgress({
            location: vscode.ProgressLocation.Notification,
            title: 'Generating image...',
            cancellable: false
        }, async () => {
            const result = await client.generateImage(prompt, model, width, height);

            // Show image URL
            const action = await vscode.window.showInformationMessage(
                `✓ Image generated | Cost: $${result.cost.toFixed(4)}`,
                'Open URL',
                'Copy URL'
            );

            if (action === 'Open URL') {
                vscode.env.openExternal(vscode.Uri.parse(result.url));
            } else if (action === 'Copy URL') {
                vscode.env.clipboard.writeText(result.url);
                vscode.window.showInformationMessage('URL copied to clipboard');
            }

            refresh();
        });
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function showBalance() {
    if (!ensureClientInitialized()) return;

    try {
        const result = await client.getBalance();
        vscode.window.showInformationMessage(
            `Balance: $${result.balance.toFixed(2)} ${result.currency}`
        );
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function showUsage() {
    if (!ensureClientInitialized()) return;

    try {
        const result = await client.getUsage();
        vscode.window.showInformationMessage(
            `Usage (${result.period}): ${result.total_requests} requests | $${result.total_cost.toFixed(2)}`
        );
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function predictCost() {
    if (!ensureClientInitialized()) return;

    try {
        const result = await client.predictCost();

        const message = `Cost Prediction:\n` +
            `Current Month: $${result.current_month.toFixed(2)}\n` +
            `Predicted Next Month: $${result.predicted_next_month.toFixed(2)}\n` +
            `Trend: ${result.trend}\n` +
            `Confidence: ${(result.confidence * 100).toFixed(1)}%`;

        vscode.window.showInformationMessage(message);
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

async function detectAnomalies() {
    if (!ensureClientInitialized()) return;

    try {
        const anomalies = await client.detectAnomalies(30);

        if (anomalies.length === 0) {
            vscode.window.showInformationMessage('No anomalies detected');
        } else {
            const message = `Detected ${anomalies.length} anomalies in the last 30 days`;
            vscode.window.showWarningMessage(message);
        }
    } catch (error: any) {
        vscode.window.showErrorMessage(`Error: ${error.message}`);
    }
}

function refresh() {
    accountExplorerProvider.refresh();
    insightsProvider.refresh();
}

function ensureClientInitialized(): boolean {
    if (!client) {
        vscode.window.showErrorMessage('Please configure your Money API key first');
        vscode.commands.executeCommand('money-api.configure');
        return false;
    }
    return true;
}
