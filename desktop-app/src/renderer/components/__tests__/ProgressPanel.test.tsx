import '@testing-library/jest-dom';
import { render, screen } from '@testing-library/react';
import { ProgressPanel } from '../ProgressPanel';

describe('ProgressPanel Component', () => {
    const mockAgentHealth = {
        'scout-coordinator': 'healthy' as const,
        'data-enrichment': 'healthy' as const,
        'quality-focused': 'healthy' as const,
        'proactive-scanning': 'unhealthy' as const
    };

    test('displays no search message when pipeline is null', () => {
        render(<ProgressPanel pipeline={null} agentHealth={{}} />);

        expect(screen.getByText(/Enter a job description/i)).toBeInTheDocument();
    });

    test('displays pipeline status', () => {
        const pipeline = {
            status: 'scanning' as const,
            progress: 45,
            activities: []
        };

        render(<ProgressPanel pipeline={pipeline} agentHealth={mockAgentHealth} />);

        expect(screen.getByText(/Scanning for Candidates/i)).toBeInTheDocument();
        expect(screen.getByText('45%')).toBeInTheDocument();
    });

    test('shows recent activities', () => {
        const pipeline = {
            status: 'enriching' as const,
            progress: 60,
            activities: [
                {
                    timestamp: '10:30',
                    type: 'success' as const,
                    icon: '✅',
                    message: 'Found 5 candidates on GitHub'
                },
                {
                    timestamp: '10:31',
                    type: 'info' as const,
                    icon: 'ℹ️',
                    message: 'Enriching candidate profiles'
                }
            ]
        };

        render(<ProgressPanel pipeline={pipeline} agentHealth={mockAgentHealth} />);

        expect(screen.getByText(/Found 5 candidates on GitHub/i)).toBeInTheDocument();
        expect(screen.getByText(/Enriching candidate profiles/i)).toBeInTheDocument();
    });

    test('displays agent health status', () => {
        const pipeline = {
            status: 'scanning' as const,
            progress: 20,
            activities: []
        };

        render(<ProgressPanel pipeline={pipeline} agentHealth={mockAgentHealth} />);

        expect(screen.getByText(/Scout Coordinator/i)).toBeInTheDocument();
        expect(screen.getByText(/Data Enrichment/i)).toBeInTheDocument();
        expect(screen.getByText(/Quality Focused/i)).toBeInTheDocument();
        expect(screen.getByText(/Proactive Scanning/i)).toBeInTheDocument();
    });

    test('shows success message when completed', () => {
        const pipeline = {
            status: 'completed' as const,
            progress: 100,
            activities: []
        };

        render(<ProgressPanel pipeline={pipeline} agentHealth={mockAgentHealth} />);

        expect(screen.getByText(/Search completed/i)).toBeInTheDocument();
    });

    test('shows error message when failed', () => {
        const pipeline = {
            status: 'failed' as const,
            progress: 50,
            activities: []
        };

        render(<ProgressPanel pipeline={pipeline} agentHealth={mockAgentHealth} />);

        expect(screen.getByText(/Search failed/i)).toBeInTheDocument();
    });

    test('displays only last 5 activities', () => {
        const activities = Array.from({ length: 10 }, (_, i) => ({
            timestamp: `10:${i}`,
            type: 'info' as const,
            icon: 'ℹ️',
            message: `Activity ${i}`
        }));

        const pipeline = {
            status: 'scanning' as const,
            progress: 30,
            activities
        };

        render(<ProgressPanel pipeline={pipeline} agentHealth={mockAgentHealth} />);

        // Should show activities 5-9 (last 5)
        expect(screen.getByText(/Activity 9/i)).toBeInTheDocument();
        expect(screen.getByText(/Activity 5/i)).toBeInTheDocument();
        expect(screen.queryByText(/Activity 4/i)).not.toBeInTheDocument();
    });

    test('formats agent names correctly', () => {
        const pipeline = {
            status: 'scanning' as const,
            progress: 10,
            activities: []
        };

        render(<ProgressPanel pipeline={pipeline} agentHealth={{
            'scout-coordinator': 'healthy',
            'data-enrichment-agent': 'healthy'
        }} />);

        expect(screen.getByText('Scout Coordinator')).toBeInTheDocument();
        expect(screen.getByText('Data Enrichment Agent')).toBeInTheDocument();
    });
});
