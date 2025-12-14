import { Link } from 'react-router-dom';
import { Video, Users, BarChart3, Sparkles } from 'lucide-react';
import { ServiceStatus } from './ServiceStatus';

export const Header = () => {
  return (
    <header className="bg-white shadow-sm border-b">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between mb-4">
          <Link to="/" className="flex items-center space-x-2">
            <Video className="h-8 w-8 text-blue-600" />
            <span className="text-xl font-bold text-gray-900">TalentAI Interview</span>
          </Link>

          <ServiceStatus />
        </div>

        <nav className="flex items-center space-x-6">
          <Link
            to="/"
            className="flex items-center space-x-1 text-gray-600 hover:text-blue-600 transition-colors"
          >
            <Users className="h-4 w-4" />
            <span>Dashboard</span>
          </Link>
          <Link
            to="/question-builder"
            className="flex items-center space-x-1 text-gray-600 hover:text-blue-600 transition-colors"
          >
            <Sparkles className="h-4 w-4" />
            <span>Question Builder</span>
          </Link>
          <Link
            to="/results"
            className="flex items-center space-x-1 text-gray-600 hover:text-blue-600 transition-colors"
          >
            <BarChart3 className="h-4 w-4" />
            <span>Results</span>
          </Link>
        </nav>
      </div>
    </header>
  );
};