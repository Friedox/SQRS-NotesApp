import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

// mock react-router-dom module completely
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    MemoryRouter: ({ children }) => <>{children}</>,
    Routes: ({ children }) => <>{children}</>,
    Route: ({ element }) => element,
    useNavigate: () => mockNavigate,
}));

import Create from './Create';

beforeAll(() => {
    window.alert = jest.fn();
});
beforeEach(() => {
    sessionStorage.clear();
    // Always set user to avoid JSON.parse null
    sessionStorage.setItem('user', JSON.stringify({ name: 'Tester' }));
    // Only auth_token missing tests override auth_token
    sessionStorage.setItem('auth_token', 'token123');
    jest.restoreAllMocks();
    mockNavigate.mockClear();
});

describe('Create Component', () => {
    it('renders editor toolbar and inputs', () => {
        render(
            <Create />
        );
        expect(screen.getByPlaceholderText(/note title/i)).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/write your note here/i)).toBeInTheDocument();
        expect(screen.getByAltText(/Translate/i)).toBeInTheDocument();
        expect(screen.getByAltText(/Bold/i)).toBeInTheDocument();
        expect(screen.getByAltText(/Italic/i)).toBeInTheDocument();
    });

    it('saves a new note and navigates', async () => {
        jest.spyOn(global, 'fetch').mockResolvedValueOnce({
            ok: true,
            json: async () => ({ detail: { id: 1, title: 'Test', content: '<p>Test</p>' } }),
        });

        render(
            <Create />
        );

        fireEvent.change(screen.getByPlaceholderText(/note title/i), { target: { value: 'Hello' } });
        const contentDiv = screen.getByPlaceholderText(/write your note here/i);
        fireEvent.input(contentDiv, { target: { innerHTML: '<p>Hello</p>' } });
        fireEvent.click(screen.getByText(/save/i));

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/api/v1/notes/'),
                expect.objectContaining({ method: 'POST' })
            );
        });

        expect(mockNavigate).toHaveBeenCalledWith('/notes');
        expect(window.alert).toHaveBeenCalledWith('Note saved successfully!');
    });

    it('alerts when no auth token', () => {
        // simulate missing auth_token: clear storage and keep only user
        sessionStorage.clear();
        sessionStorage.setItem('user', JSON.stringify({ name: 'Tester' }));

        render(
            <Create />
        );

        fireEvent.click(screen.getByText(/save/i));
        expect(window.alert).toHaveBeenCalledWith('Enter in the system, please');
        expect(mockNavigate).not.toHaveBeenCalled();
    });
});
