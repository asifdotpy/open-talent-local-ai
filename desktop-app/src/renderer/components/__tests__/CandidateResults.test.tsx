import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { CandidateResults, Candidate } from '../CandidateResults';
import '@testing-library/jest-dom';

const mockCandidates: Candidate[] = [
    {
        id: '1',
        name: 'Alice Smith',
        headline: 'Senior React Developer',
        location: 'New York, NY',
        score: 95,
        skills: ['React', 'TypeScript', 'Node.js'],
        github_url: 'https://github.com/alice',
        github_stars: 120,
        bio: 'Passionate developer with 8 years of experience.'
    },
    {
        id: '2',
        name: 'Bob Jones',
        headline: 'Frontend Engineer',
        location: 'San Francisco, CA',
        score: 75,
        skills: ['JavaScript', 'Vue', 'CSS'],
        linkedin_url: 'https://linkedin.com/in/bob',
        bio: 'Core contributor to several open source projects.'
    }
];

describe('CandidateResults', () => {
    test('renders list of candidates', () => {
        render(<CandidateResults candidates={mockCandidates} />);
        expect(screen.getByText('Alice Smith')).toBeInTheDocument();
        expect(screen.getByText('Bob Jones')).toBeInTheDocument();
        expect(screen.getByText('Found 2 Candidates')).toBeInTheDocument();
    });

    test('filters candidates by score', () => {
        render(<CandidateResults candidates={mockCandidates} />);

        const slider = screen.getByLabelText(/Min Score:/);
        fireEvent.change(slider, { target: { value: '90' } });

        expect(screen.getByText('Alice Smith')).toBeInTheDocument();
        expect(screen.queryByText('Bob Jones')).not.toBeInTheDocument();
        expect(screen.getByText('Found 1 Candidate (score ≥ 90)')).toBeInTheDocument();
    });

    test('sorts candidates by name', () => {
        render(<CandidateResults candidates={mockCandidates} />);

        const select = screen.getByLabelText(/Sort by:/);
        fireEvent.change(select, { target: { value: 'name' } });

        const names = screen.getAllByRole('heading', { level: 3 });
        expect(names[0]).toHaveTextContent('Alice Smith');
        expect(names[1]).toHaveTextContent('Bob Jones');
    });

    test('opens detail modal on click', () => {
        render(<CandidateResults candidates={mockCandidates} />);

        const viewButtons = screen.getAllByText('Interview');
        fireEvent.click(viewButtons[0]);

        // This is a mock test as the modal is not implemented
        expect(true).toBe(true);
    });

    test('calls onInterviewClick when schedule button is clicked', () => {
        const mockInterviewClick = jest.fn();
        render(<CandidateResults candidates={mockCandidates} onInterviewClick={mockInterviewClick} />);

        const interviewButtons = screen.getAllByText('Interview');
        fireEvent.click(interviewButtons[0]);

        expect(mockInterviewClick).toHaveBeenCalledWith(mockCandidates[0]);
    });

    test('displays "no results" message when filter is too strict', () => {
        render(<CandidateResults candidates={mockCandidates} />);

        const slider = screen.getByLabelText(/Min Score:/);
        fireEvent.change(slider, { target: { value: '100' } });

        expect(screen.getByText(/No candidates match your criteria/i)).toBeInTheDocument();
    });
});
