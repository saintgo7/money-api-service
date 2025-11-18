import * as vscode from 'vscode';
import { MoneyAPIClient } from '../client';

export class InsightsProvider implements vscode.TreeDataProvider<InsightItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<InsightItem | undefined | null | void> = new vscode.EventEmitter<InsightItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<InsightItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor(private client: MoneyAPIClient) {}

    updateClient(client: MoneyAPIClient) {
        this.client = client;
        this.refresh();
    }

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: InsightItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: InsightItem): Promise<InsightItem[]> {
        if (!this.client) {
            return [];
        }

        if (!element) {
            try {
                const insights = await this.client.getInsights();
                const items: InsightItem[] = [];

                // Add recommendations
                if (insights.recommendations && insights.recommendations.length > 0) {
                    items.push(new InsightItem(
                        `Recommendations (${insights.recommendations.length})`,
                        vscode.TreeItemCollapsibleState.Expanded,
                        'recommendations'
                    ));
                }

                // Add cost breakdown
                if (insights.cost_breakdown && insights.cost_breakdown.length > 0) {
                    items.push(new InsightItem(
                        'Top Endpoints by Cost',
                        vscode.TreeItemCollapsibleState.Expanded,
                        'cost_breakdown'
                    ));
                }

                return items;
            } catch (error: any) {
                return [new InsightItem(`Error: ${error.message}`, vscode.TreeItemCollapsibleState.None)];
            }
        }

        // Child items
        try {
            switch (element.contextValue) {
                case 'recommendations':
                    return await this.getRecommendationItems();
                case 'cost_breakdown':
                    return await this.getCostBreakdownItems();
                default:
                    return [];
            }
        } catch (error: any) {
            return [new InsightItem(`Error: ${error.message}`, vscode.TreeItemCollapsibleState.None)];
        }
    }

    private async getRecommendationItems(): Promise<InsightItem[]> {
        const insights = await this.client.getInsights();
        return insights.recommendations.map(rec => {
            const icon = this.getIconForPriority(rec.priority);
            return new InsightItem(
                `${icon} [${rec.priority.toUpperCase()}] ${rec.message}`,
                vscode.TreeItemCollapsibleState.None,
                'recommendation'
            );
        });
    }

    private async getCostBreakdownItems(): Promise<InsightItem[]> {
        const insights = await this.client.getInsights();
        return insights.cost_breakdown.slice(0, 10).map(item => {
            return new InsightItem(
                `${item.endpoint}: $${item.cost.toFixed(2)} (${item.percentage.toFixed(1)}%)`,
                vscode.TreeItemCollapsibleState.None,
                'cost_item'
            );
        });
    }

    private getIconForPriority(priority: string): string {
        switch (priority.toLowerCase()) {
            case 'high':
                return '🔴';
            case 'medium':
                return '🟡';
            case 'low':
                return '🟢';
            default:
                return '⚪';
        }
    }
}

class InsightItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState,
        public readonly contextValue?: string
    ) {
        super(label, collapsibleState);
        this.tooltip = label;
    }
}
