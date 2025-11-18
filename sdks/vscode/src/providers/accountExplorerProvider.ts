import * as vscode from 'vscode';
import { MoneyAPIClient } from '../client';

export class AccountExplorerProvider implements vscode.TreeDataProvider<TreeItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<TreeItem | undefined | null | void> = new vscode.EventEmitter<TreeItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<TreeItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private client: MoneyAPIClient) {}

    updateClient(client: MoneyAPIClient) {
        this.client = client;
        this.refresh();
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: TreeItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: TreeItem): Promise<TreeItem[]> {
        if (!this.client) {
            return [new TreeItem('Configure API Key', vscode.TreeItemCollapsibleState.None)];
        }

        if (!element) {
            // Root items
            return [
                new TreeItem('Account Balance', vscode.TreeItemCollapsibleState.Collapsed, 'balance'),
                new TreeItem('Usage Statistics', vscode.TreeItemCollapsibleState.Collapsed, 'usage'),
                new TreeItem('Cost Prediction', vscode.TreeItemCollapsibleState.Collapsed, 'prediction')
            ];
        }

        // Child items
        try {
            switch (element.contextValue) {
                case 'balance':
                    return await this.getBalanceItems();
                case 'usage':
                    return await this.getUsageItems();
                case 'prediction':
                    return await this.getPredictionItems();
                default:
                    return [];
            }
        } catch (error: any) {
            return [new TreeItem(`Error: ${error.message}`, vscode.TreeItemCollapsibleState.None)];
        }
    }

    private async getBalanceItems(): Promise<TreeItem[]> {
        const balance = await this.client.getBalance();
        return [
            new TreeItem(`$${balance.balance.toFixed(2)} ${balance.currency}`, vscode.TreeItemCollapsibleState.None)
        ];
    }

    private async getUsageItems(): Promise<TreeItem[]> {
        const usage = await this.client.getUsage();
        return [
            new TreeItem(`Requests: ${usage.total_requests}`, vscode.TreeItemCollapsibleState.None),
            new TreeItem(`Cost: $${usage.total_cost.toFixed(2)}`, vscode.TreeItemCollapsibleState.None),
            new TreeItem(`Period: ${usage.period}`, vscode.TreeItemCollapsibleState.None)
        ];
    }

    private async getPredictionItems(): Promise<TreeItem[]> {
        const prediction = await this.client.predictCost();
        return [
            new TreeItem(`Current: $${prediction.current_month.toFixed(2)}`, vscode.TreeItemCollapsibleState.None),
            new TreeItem(`Predicted: $${prediction.predicted_next_month.toFixed(2)}`, vscode.TreeItemCollapsibleState.None),
            new TreeItem(`Trend: ${prediction.trend}`, vscode.TreeItemCollapsibleState.None),
            new TreeItem(`Confidence: ${(prediction.confidence * 100).toFixed(1)}%`, vscode.TreeItemCollapsibleState.None)
        ];
    }
}

class TreeItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly contextValue?: string
    ) {
        super(label, collapsibleState);
        this.tooltip = label;
    }
}
