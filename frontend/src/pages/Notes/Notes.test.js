import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

// Мокаем useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
    useNavigate: () => mockNavigate,
}));

import Notes from './Notes';

beforeAll(() => {
    window.alert = jest.fn();
    jest.spyOn(console, 'error').mockImplementation(() => {});
});

beforeEach(() => {
    jest.clearAllMocks();
    sessionStorage.clear();
    // По умолчанию хранить и user, и auth_token
    sessionStorage.setItem('user', JSON.stringify({ name: 'Tester' }));
    sessionStorage.setItem('auth_token', 'token123');
});

describe('Notes Component', () => {
    it('fetches and displays list of notes', async () => {
        const mockNotes = [
            { note_id: '1', title: 'Note 1', updated_at: '2025-05-01T12:00:00Z' },
            { note_id: '2', title: 'Note 2', updated_at: '2025-05-02T15:30:00Z' },
        ];
        jest.spyOn(global, 'fetch').mockResolvedValueOnce({
            ok: true,
            json: async () => ({ detail: mockNotes }),
        });

        render(<Notes />);

        await waitFor(() =>
            expect(global.fetch).toHaveBeenCalledWith(
                expect.stringContaining('/api/v1/notes/'),
                expect.objectContaining({ method: 'GET' })
            )
        );

        expect(await screen.findByText('Note 1')).toBeInTheDocument();
        expect(await screen.findByText('Note 2')).toBeInTheDocument();
    });

    it('navigates to create page on create button click', () => {
        jest.spyOn(global, 'fetch').mockResolvedValue({ ok: true, json: async () => ({ detail: [] }) });

        render(<Notes />);
        fireEvent.click(screen.getByRole('button', { name: /create note/i }));
        expect(mockNavigate).toHaveBeenCalledWith('/create');
    });

    it('navigates to edit page on note click', async () => {
        const mockNotes = [{ note_id: '1', title: 'Note 1', updated_at: '2025-05-01T12:00:00Z' }];
        jest.spyOn(global, 'fetch').mockResolvedValueOnce({
            ok: true,
            json: async () => ({ detail: mockNotes }),
        });

        render(<Notes />);
        const noteBtn = await screen.findByText('Note 1');
        fireEvent.click(noteBtn.closest('button'));
        expect(mockNavigate).toHaveBeenCalledWith('/edit', { state: { noteId: '1' } });
    });

    it('deletes a note and updates list', async () => {
        const mockNotes = [
            { note_id: '1', title: 'To delete', updated_at: '2025-05-01T12:00:00Z' },
            { note_id: '2', title: 'To keep',  updated_at: '2025-05-02T15:30:00Z' },
        ];
        // 1) GET, 2) DELETE
        jest.spyOn(global, 'fetch')
            .mockResolvedValueOnce({ ok: true, json: async () => ({ detail: mockNotes }) })
            .mockResolvedValueOnce({ ok: true });

        const { container } = render(<Notes />);
        // Ждём, пока пришли заметки
        await screen.findByText('To delete');

        // Находим кнопку удаления по классу .note_delete
        const deleteBtns = container.getElementsByClassName('note_delete');
        expect(deleteBtns.length).toBe(2);

        // Кликаем по первой
        fireEvent.click(deleteBtns[0]);

        // Ожидаем, что DELETE-запрос был выполнен
        await waitFor(() => {
            expect(global.fetch).toHaveBeenLastCalledWith(
                expect.stringContaining('/api/v1/notes/1'),
                expect.objectContaining({ method: 'DELETE' })
            );
        });

        // Первая заметка исчезла, вторая осталась
        await waitFor(() => {
            expect(screen.queryByText('To delete')).not.toBeInTheDocument();
        });
        expect(screen.getByText('To keep')).toBeInTheDocument();
    });

});
