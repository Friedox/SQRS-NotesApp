import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

// Mock react-router-dom including useLocation and useNavigate
const mockNavigate = jest.fn();
const mockState = { noteId: '123' };
jest.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
    useLocation: () => ({ state: mockState }),
}));

import Edit from './Edit';

beforeAll(() => {
    window.alert = jest.fn();
    jest.spyOn(console, 'error').mockImplementation(() => {});
});
beforeEach(() => {
    sessionStorage.clear();
    sessionStorage.setItem('user', JSON.stringify({ name: 'Tester' }));
    sessionStorage.setItem('auth_token', 'token123');
    mockNavigate.mockClear();
});

describe('Edit Component', () => {
    it('fetches and displays existing note', async () => {
        const mockDetail = { title: 'Old Title', content: '<p>Old Content</p>' };
        jest.spyOn(global, 'fetch')
            .mockResolvedValueOnce({ ok: true, json: async () => ({ detail: mockDetail }) });

        render(<Edit />);

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/api/v1/notes/123'),
                expect.objectContaining({ method: 'GET' })
            );
        });

        const titleInput = await screen.findByDisplayValue('Old Title');
        expect(titleInput).toBeInTheDocument();

        const contentDiv = screen.getByPlaceholderText(/Write your note here/i);
        expect(contentDiv.innerHTML).toBe(mockDetail.content);
    });

    it('saves edited note and navigates', async () => {
        jest.spyOn(global, 'fetch')
            .mockResolvedValueOnce({ ok: true, json: async () => ({ detail: { title: 'T1', content: '<p>C1</p>' } }) })
            .mockResolvedValueOnce({ ok: true, json: async () => ({ detail: {} }) });

        render(<Edit />);

        const titleInput = await screen.findByDisplayValue('T1');
        fireEvent.change(titleInput, { target: { value: 'New Title' } });

        const contentDiv = screen.getByPlaceholderText(/Write your note here/i);
        fireEvent.input(contentDiv, { target: { innerHTML: '<p>New</p>' } });

        fireEvent.click(screen.getByText(/save/i));

        await waitFor(() => {
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/api/v1/notes/123'),
                expect.objectContaining({ method: 'PATCH' })
            );
        });

        expect(mockNavigate).toHaveBeenCalledWith('/notes');
    });

    it('does not perform save without auth token', async () => {
        // simulate note load OK then missing auth_token
        sessionStorage.clear();
        sessionStorage.setItem('user', JSON.stringify({ name: 'Tester' }));

        jest.spyOn(global, 'fetch')
            // initial GET
            .mockResolvedValueOnce({ ok: true, json: async () => ({ detail: { title: 'T1', content: '<p>C1</p>' } }) })
            // PATCH even without token
            .mockResolvedValueOnce({ ok: true, json: async () => ({ detail: {} }) });

        render(<Edit />);

        fireEvent.click(screen.getByText(/save/i));
        // two calls: GET and PATCH
        expect(global.fetch).toHaveBeenCalledTimes(2);
        expect(mockNavigate).not.toHaveBeenCalled();
    });
});
