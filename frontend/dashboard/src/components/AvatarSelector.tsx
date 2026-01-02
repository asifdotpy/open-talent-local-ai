/**
 * Avatar Selector Component
 * Shows available avatars with dropdown selection
 */

import { useInterviewStore } from '../stores/interviewStore';

export function AvatarSelector() {
  const { currentAvatar, availableAvatars, selectAvatar, initializeAvatars } = useInterviewStore();

  const handleAvatarChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const avatarId = e.target.value;
    const avatar = availableAvatars.find(a => a.id === avatarId);
    if (avatar) {
      selectAvatar(avatar);
    }
  };

  const handleRefresh = async () => {
    try {
      await initializeAvatars();
    } catch (error) {
      console.error('Failed to refresh avatars:', error);
    }
  };

  return (
    <div className="avatar-selector">
      <h3 className="text-lg font-semibold mb-4">Interview Avatar</h3>

      {availableAvatars.length > 0 ? (
        <div className="space-y-4">
          {/* Avatar Dropdown */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Select Avatar
            </label>
            <select
              value={currentAvatar?.id || ''}
              onChange={handleAvatarChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
            >
              {availableAvatars.map((avatar) => (
                <option key={avatar.id} value={avatar.id}>
                  {avatar.name} {avatar.hasFullLipSync ? '✅' : ''} ({avatar.morphTargetType})
                </option>
              ))}
            </select>
          </div>

          {/* Current Avatar Display */}
          {currentAvatar && (
            <div className="flex items-center space-x-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <div className="w-16 h-16 bg-gray-300 rounded flex items-center justify-center text-xs font-medium">
                {currentAvatar.morphTargetType}
              </div>
              <div className="flex-1">
                <h4 className="font-medium">{currentAvatar.name}</h4>
                <p className="text-sm text-gray-600">
                  {currentAvatar.morphTargetType} • {currentAvatar.isLocal ? 'Local' : 'Remote'}
                </p>
                <div className="flex items-center mt-1 space-x-2">
                  <span className="text-xs px-2 py-1 bg-blue-100 text-blue-700 rounded">
                    {currentAvatar.morphTargetType}
                  </span>
                  {currentAvatar.hasFullLipSync && (
                    <span className="text-xs px-2 py-1 bg-green-100 text-green-700 rounded">
                      ✅ Full Lip-Sync
                    </span>
                  )}
                  {currentAvatar.isLocal && (
                    <span className="text-xs px-2 py-1 bg-purple-100 text-purple-700 rounded">
                      📁 Local
                    </span>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      ) : (
        <div className="text-center p-8">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto mb-4"></div>
          <p className="text-gray-600 mb-4">Loading avatars...</p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600"
          >
            Retry Loading
          </button>
        </div>
      )}
    </div>
  );
}
