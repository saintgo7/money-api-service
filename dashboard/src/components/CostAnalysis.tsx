'use client';

export function CostAnalysis({ apiKey }: { apiKey: string }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-bold mb-4">Cost Analysis</h2>
      <p className="text-gray-600">
        Detailed cost breakdown and trends coming soon.
      </p>
      <div className="mt-4 p-4 bg-gray-50 rounded-lg">
        <p className="text-sm text-gray-700">
          💡 Tip: Monitor your usage regularly to optimize costs.
          Consider upgrading to a higher tier for volume discounts.
        </p>
      </div>
    </div>
  );
}
