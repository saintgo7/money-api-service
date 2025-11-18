interface HeaderProps {
  userData: any;
  onLogout: () => void;
}

export function Header({ userData, onLogout }: HeaderProps) {
  return (
    <header className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Money API Service</h1>
          <p className="text-sm text-gray-600">Developer Dashboard</p>
        </div>
        <div className="flex items-center gap-4">
          {userData && (
            <div className="text-right">
              <p className="text-sm font-medium">{userData.email}</p>
              <p className="text-xs text-gray-500">{userData.plan} Plan</p>
            </div>
          )}
          <button
            onClick={onLogout}
            className="px-4 py-2 text-sm bg-red-600 text-white rounded-lg hover:bg-red-700"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  );
}
