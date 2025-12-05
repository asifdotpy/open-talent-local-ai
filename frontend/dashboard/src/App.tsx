import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { InterviewDashboard } from './components/InterviewDashboard';
import { InterviewInterface } from './components/InterviewInterface';
import { ResultsPage } from './components/ResultsPage';
import { QuestionBuilder } from './components/question-builder/QuestionBuilder';
import { Header } from './components/Header';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Header />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<InterviewDashboard />} />
            <Route path="/interview" element={<InterviewInterface />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/question-builder" element={<QuestionBuilder />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
