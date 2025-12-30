import '@testing-library/jest-dom';
import { render, screen, fireEvent } from '@testing-library/react';
import { SearchPrompt } from '../SearchPrompt';

describe('SearchPrompt Component', () => {
    const mockOnSearch = jest.fn();

    beforeEach(() => {
        mockOnSearch.mockClear();
    });

    test('renders prompt textarea', () => {
        render(<SearchPrompt onSearch={mockOnSearch} isSearching={false} />);

        const textarea = screen.getByPlaceholderText(/Describe the candidate/i);
        expect(textarea).toBeInTheDocument();
    });

    test('calls onSearch with prompt and selected tools', () => {
        render(<SearchPrompt onSearch={mockOnSearch} isSearching={false} />);

        const textarea = screen.getByPlaceholderText(/Describe the candidate/i);
        fireEvent.change(textarea, {
            target: { value: 'Senior React developer in NYC' }
        });

        const searchButton = screen.getByRole('button', { name: /Search Candidates/ });
        fireEvent.click(searchButton);

        expect(mockOnSearch).toHaveBeenCalledWith({
            prompt: 'Senior React developer in NYC',
            tools: expect.arrayContaining(['github', 'stackoverflow', 'googleXray'])
        });
    });

    test('disables button when searching', () => {
        render(<SearchPrompt onSearch={mockOnSearch} isSearching={true} />);

        const searchButton = screen.getByRole('button', { name: /Searching/ });
        expect(searchButton).toBeDisabled();
    });

    test('disables button when prompt is empty', () => {
        render(<SearchPrompt onSearch={mockOnSearch} isSearching={false} />);

        const searchButton = screen.getByRole('button', { name: /Search Candidates/ });
        expect(searchButton).toBeDisabled();
    });

    test('toggles tool selection', () => {
        render(<SearchPrompt onSearch={mockOnSearch} isSearching={false} />);

        // GitHub should be checked by default
        const githubCheckbox = screen.getByLabelText(/GitHub/i) as HTMLInputElement;
        expect(githubCheckbox.checked).toBe(true);

        // Uncheck GitHub
        fireEvent.click(githubCheckbox);
        expect(githubCheckbox.checked).toBe(false);

        // ContactOut should be unchecked by default
        const contactoutCheckbox = screen.getByLabelText(/ContactOut/i) as HTMLInputElement;
        expect(contactoutCheckbox.checked).toBe(false);

        // Check ContactOut
        fireEvent.click(contactoutCheckbox);
        expect(contactoutCheckbox.checked).toBe(true);
    });

    test('shows loading message when searching', () => {
        render(<SearchPrompt onSearch={mockOnSearch} isSearching={true} />);

        expect(screen.getByText(/Your search is running in the background/i)).toBeInTheDocument();
    });

    test('trims whitespace from prompt', () => {
        render(<SearchPrompt onSearch={mockOnSearch} isSearching={false} />);

        const textarea = screen.getByPlaceholderText(/Describe the candidate/i);
        fireEvent.change(textarea, {
            target: { value: '  Senior Developer  ' }
        });

        const searchButton = screen.getByRole('button', { name: /Search Candidates/ });
        fireEvent.click(searchButton);

        expect(mockOnSearch).toHaveBeenCalledWith(
            expect.objectContaining({
                prompt: 'Senior Developer'
            })
        );
    });
});
