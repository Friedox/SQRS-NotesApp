const React = require('react');

const MemoryRouter = ({ children }) => <>{children}</>;

const Routes = ({ children }) => <>{children}</>;
const Route = ({ element }) => element;

const useNavigate = () => {
    return jest.fn();
};
const useLocation = () => ({ pathname: '/' });
const useParams = () => ({});

module.exports = {
    MemoryRouter,
    Routes,
    Route,
    useNavigate,
    useLocation,
    useParams,
    BrowserRouter: MemoryRouter,
    Link: ({ children }) => <>{children}</>,
};
