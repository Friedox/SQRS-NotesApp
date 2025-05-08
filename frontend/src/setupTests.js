import '@testing-library/jest-dom';
import fetchMock from 'jest-fetch-mock';
fetchMock.enableMocks();

const mockSessionStorage = (() => {
    let store = {};
    return {
        getItem: (key) => store[key] || null,
        setItem: (key, value) => { store[key] = value.toString(); },
        removeItem(key) { delete this.store[key]; },
        clear: () => { store = {}; },
    };
})();

Object.defineProperty(window, 'sessionStorage', {
    value: mockSessionStorage,
});

// Перед каждым тестом закидываем «юзера» в sessionStorage
beforeEach(() => {
    window.sessionStorage.clear();
    window.sessionStorage.setItem('user', JSON.stringify({ name: 'Test User' }));
});