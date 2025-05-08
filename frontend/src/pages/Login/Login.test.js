import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import Login from './Login';

beforeEach(() => {
    sessionStorage.clear();
    jest.restoreAllMocks();
});

describe('Login Component', () => {
    it('renders login form by default with disabled submit', () => {
        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );

        const emailInput = screen.getByPlaceholderText(/email/i);
        const passwordInput = screen.getByPlaceholderText(/password/i);
        const submitButton = screen.getByRole('button', { name: /login/i });

        expect(emailInput).toBeInTheDocument();
        expect(passwordInput).toBeInTheDocument();
        expect(submitButton).toBeDisabled();
    });

    it('toggles to register form when clicking toggle button', () => {
        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );

        const toggleButton = screen.getByRole('button', { name: /don't have an account\? register/i });
        fireEvent.click(toggleButton);

        expect(screen.getByPlaceholderText(/name/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /register/i })).toBeDisabled();
    });

    it('enables submit when fields are filled', () => {
        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );

        const email = screen.getByPlaceholderText(/email/i);
        const password = screen.getByPlaceholderText(/password/i);
        const button = screen.getByRole('button', { name: /login/i });

        fireEvent.change(email, { target: { value: 'user@test.com' } });
        fireEvent.change(password, { target: { value: 'pass' } });

        expect(button).toBeEnabled();
    });

    it('successful login stores token and navigates', async () => {
        // mock fetch response
        jest.spyOn(global, 'fetch').mockResolvedValueOnce({
            ok: true,
            json: async () => ({ detail: { auth_token: 'abc123', new_user: { name: 'User' } } }),
        });

        render(
            <MemoryRouter initialEntries={["/"]}>
                <Routes>
                    <Route path="/" element={<Login />} />
                    <Route path="/notes" element={<div>NOTES PAGE</div>} />
                </Routes>
            </MemoryRouter>
        );

        fireEvent.change(screen.getByPlaceholderText(/email/i), { target: { value: 'a@b.c' } });
        fireEvent.change(screen.getByPlaceholderText(/password/i), { target: { value: 'pwd' } });
        fireEvent.click(screen.getByRole('button', { name: /login/i }));

        await waitFor(() => {
            expect(screen.getByText(/notes page/i)).toBeInTheDocument();
        });

        expect(sessionStorage.getItem('auth_token')).toBe('abc123');
        const storedUser = JSON.parse(sessionStorage.getItem('user'));
        expect(storedUser).toEqual({ name: 'User' });
    });

    it('shows error message on failed login', async () => {
        // mock fetch failure
        jest.spyOn(global, 'fetch').mockResolvedValueOnce({
            ok: false,
            status: 401,
            json: async () => ({ detail: 'invalid credentials' }),
        });

        render(
            <MemoryRouter>
                <Login />
            </MemoryRouter>
        );

        fireEvent.change(screen.getByPlaceholderText(/email/i), { target: { value: 'x@x.x' } });
        fireEvent.change(screen.getByPlaceholderText(/password/i), { target: { value: 'wrong' } });
        fireEvent.click(screen.getByRole('button', { name: /login/i }));

        const error = await screen.findByText(/invalid credentials/i);
        expect(error).toBeInTheDocument();
    });
});
