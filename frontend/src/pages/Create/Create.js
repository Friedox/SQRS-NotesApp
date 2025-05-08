// Import necessary React hooks and libraries
import React, {useState, useRef, useEffect} from 'react';
import {useNavigate} from 'react-router-dom';

// Import CSS styles
import './style.css';
import '../../style/style.css';
import '../Notes/style.css';

// Import icons and images
import boldIcon from '../../assets/icon/bold-02.svg';
import italicIcon from '../../assets/icon/italic-02.svg';
import underlineIcon from '../../assets/icon/underline-02.svg';
import strikethroughIcon from '../../assets/icon/strikethrough-02.svg';
import translateIcon from '../../assets/icon/translate-01.svg';
import mkad from "../../assets/icon/MKAD.svg";
import account from "../../assets/illustration/account.svg";

// Base API URL from environment variable
const API_BASE = process.env.REACT_APP_API_BASE_URL;

function Create() {
    const navigate = useNavigate();

    // State for note title and content
    const [title, setTitle] = useState('');
    const [content, setContent] = useState('');
    const contentRef = useRef(null); // Ref to access the contentEditable div

    // Formatting button states
    const [boldActive, setBoldActive] = useState(false);
    const [italicActive, setItalicActive] = useState(false);
    const [underlineActive, setUnderlineActive] = useState(false);
    const [strikeActive, setStrikeActive] = useState(false);
    const [h1Active, setH1Active] = useState(false);
    const [h2Active, setH2Active] = useState(false);
    const [h3Active, setH3Active] = useState(false);
    const [currentColor, setCurrentColor] = useState('#000000');

    // Language selection for translation
    const [sourceLang, setSourceLang] = useState('auto');
    const [targetLang, setTargetLang] = useState('ru');

    // Color palette for text
    const colors = ['#000000', '#FF0000', '#00AA00', '#0000FF', '#FFA500', '#800080'];

    // Function to save note to the backend
    const handleSave = async () => {
        const token = sessionStorage.getItem('auth_token');
        if (!token) {
            alert("Enter in the system, please");
            return;
        }
        try {
            const response = await fetch(`${API_BASE}/api/v1/notes/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`,
                },
                body: JSON.stringify({title, content}),
            });
            console.log(JSON.stringify({title, content}));
            if (!response.ok) {
                const errorData = await response.json();
                console.error("Save error:", errorData);
                alert("Saved Error");
                return;
            }

            const data = await response.json();
            navigate("/notes"); // Redirect to notes page
            console.log("Note saved:", data);
            alert("Note saved successfully!");
            handleCreate(); // Reset form after saving
        } catch (error) {
            console.error("Network error:", error);
            alert("Error");
        }
    };

    // Function to translate selected text using backend API
    const handleTranslate = async () => {
        const sel = window.getSelection();
        if (!sel || sel.isCollapsed) {
            alert('Select some text to translate first');
            return;
        }
        const textToTranslate = sel.toString();
        try {
            const res = await fetch(`${API_BASE}/api/v1/translation/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${sessionStorage.getItem('auth_token')}`,
                },
                body: JSON.stringify({
                    text: textToTranslate,
                    source: sourceLang,
                    target: targetLang,
                }),
            });
            if (!res.ok) throw new Error(`Translation error: ${res.status}`);

            const result = await res.json();
            const translatedText = result.detail?.translated_text;
            if (typeof translatedText !== 'string') {
                throw new Error('Unexpected translator response format');
            }

            const range = sel.getRangeAt(0);
            range.deleteContents();
            range.insertNode(document.createTextNode(translatedText));

            sel.removeAllRanges();
            setContent(contentRef.current.innerHTML);
        } catch (err) {
            console.error(err);
            alert(err.message);
        }
    };

    // Apply formatting command to selected text
    const formatText = (command, value = null) => {
        document.execCommand(command, false, value);
        updateActiveStates(); // Update active states of formatting buttons
        setContent(contentRef.current.innerHTML); // Update content state
    };

    // Update state of active formatting buttons
    const updateActiveStates = () => {
        setBoldActive(document.queryCommandState('bold'));
        setItalicActive(document.queryCommandState('italic'));
        setUnderlineActive(document.queryCommandState('underline'));
        setStrikeActive(document.queryCommandState('strikeThrough'));

        const block = document.queryCommandValue('formatBlock');
        setH1Active(block.toLowerCase() === 'h1');
        setH2Active(block.toLowerCase() === 'h2');
        setH3Active(block.toLowerCase() === 'h3');

        const foreColor = document.queryCommandValue('foreColor');
        if (foreColor) {
            const ctx = document.createElement('canvas').getContext('2d');
            ctx.fillStyle = foreColor;
            setCurrentColor(ctx.fillStyle.toUpperCase());
        }
    };

    // Add event listeners for updating formatting state on key/mouse events
    useEffect(() => {
        const ref = contentRef.current;
        if (ref) {
            ref.addEventListener('keyup', updateActiveStates);
            ref.addEventListener('mouseup', updateActiveStates);
        }
        return () => {
            if (ref) {
                ref.removeEventListener('keyup', updateActiveStates);
                ref.removeEventListener('mouseup', updateActiveStates);
            }
        };
    }, []);

    // Reset all fields and formatting to default
    const handleCreate = () => {
        setTitle('');
        if (contentRef.current) {
            contentRef.current.innerHTML = '';
            setContent('');
            setBoldActive(false);
            setItalicActive(false);
            setUnderlineActive(false);
            setStrikeActive(false);
            setH1Active(false);
            setH2Active(false);
            setH3Active(false);
            setCurrentColor('#000000');
        }
    };

    // Handle color picker change
    const handleColorChange = (e) => {
        const color = e.target.value;
        setCurrentColor(color);
        formatText('foreColor', color);
    };

    // Utility: Convert any color to HEX format
    function toHexColor(color) {
        const ctx = document.createElement('canvas').getContext('2d');
        ctx.fillStyle = color;
        return ctx.fillStyle.toUpperCase();
    }

    // Load user name from sessionStorage
    const [user_name] = useState(JSON.parse(sessionStorage.getItem('user')).name);

    // Render component
    return (
        <div className="home_block">
            <header className="App-header">
                <img src={mkad} alt="mkad"/>
                <div className="account">
                    <h3>{user_name}</h3>
                    <img src={account} alt="account"/>
                </div>
            </header>

            <div className="edit_block">
                <div className="header">
                    <div className="edit_btns">
                        {/* Translate button */}
                        <button className="edit_btn" type="button" onClick={handleTranslate}>
                            <img src={translateIcon} alt="Translate"/>
                        </button>

                        {/* Language selectors */}
                        <select className="color-picker" value={sourceLang}
                                onChange={(e) => setSourceLang(e.target.value)}>
                            <option value="auto">Auto</option>
                            <option value="en">English</option>
                            <option value="ru">Русский</option>
                        </select>
                        <select className="color-picker" value={targetLang}
                                onChange={(e) => setTargetLang(e.target.value)}>
                            <option value="ru">Русский</option>
                            <option value="en">English</option>
                        </select>

                        {/* Formatting buttons */}
                        <button className={`edit_btn ${boldActive ? 'active' : ''}`} type="button"
                                onClick={() => formatText('bold')}>
                            <img src={boldIcon} alt="Bold"/>
                        </button>
                        <button className={`edit_btn ${italicActive ? 'active' : ''}`} type="button"
                                onClick={() => formatText('italic')}>
                            <img src={italicIcon} alt="Italic"/>
                        </button>
                        <button className={`edit_btn ${underlineActive ? 'active' : ''}`} type="button"
                                onClick={() => formatText('underline')}>
                            <img src={underlineIcon} alt="Underline"/>
                        </button>
                        <button className={`edit_btn ${strikeActive ? 'active' : ''}`} type="button"
                                onClick={() => formatText('strikeThrough')}>
                            <img src={strikethroughIcon} alt="Strikethrough"/>
                        </button>

                        {/* Heading buttons */}
                        <button className={`edit_btn ${h1Active ? 'active' : ''}`} type="button"
                                onClick={() => formatText('formatBlock', h1Active ? '<P>' : '<H1>')}>
                            H1
                        </button>
                        <button className={`edit_btn ${h2Active ? 'active' : ''}`} type="button"
                                onClick={() => formatText('formatBlock', h2Active ? '<P>' : '<H2>')}>
                            H2
                        </button>
                        <button className={`edit_btn ${h3Active ? 'active' : ''}`} type="button"
                                onClick={() => formatText('formatBlock', h3Active ? '<P>' : '<H3>')}>
                            H3
                        </button>

                        {/* Color picker */}
                        <select value={currentColor} onChange={handleColorChange} className="color-picker">
                            {colors.map((col) => (
                                <option key={col} value={col} style={{backgroundColor: col, color: '#fff'}}>
                                    {col}
                                </option>
                            ))}
                        </select>
                    </div>

                    {/* Save button */}
                    <button className="save-button" onClick={handleSave}>Save</button>
                </div>

                {/* Input area for note */}
                <div className="edit_note_block">
                    <input
                        type="text"
                        className="note-title"
                        placeholder="Note Title"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                    />
                    <div
                        className="note-content"
                        contentEditable
                        ref={contentRef}
                        onInput={() => setContent(contentRef.current.innerHTML)}
                        suppressContentEditableWarning={true}
                        placeholder="Write your note here..."
                    />
                </div>
            </div>
        </div>
    );
}

// Export component
export default Create;
