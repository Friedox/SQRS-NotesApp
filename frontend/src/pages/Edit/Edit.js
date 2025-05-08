import React, { useEffect, useRef, useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import './style.css';
import '../../style/style.css';
import mkad from '../../assets/icon/MKAD.svg';
import account from '../../assets/illustration/account.svg';
import boldIcon from '../../assets/icon/bold-02.svg';
import italicIcon from '../../assets/icon/italic-02.svg';
import underlineIcon from '../../assets/icon/underline-02.svg';
import strikethroughIcon from '../../assets/icon/strikethrough-02.svg';
import translateIcon from '../../assets/icon/translate-01.svg';

const API_BASE = process.env.REACT_APP_API_BASE_URL;

function Edit() {
    const location = useLocation();
    const noteId = location.state?.noteId; // Get note ID passed via route state
    const storedUser = JSON.parse(sessionStorage.getItem('user') || '{}');
    const [user_name, setUser_name] = useState(storedUser.name || '');
    const [title, setTitle] = useState('Title'); // Note title state
    const [content, setContent] = useState(''); // Note content state
    const contentRef = useRef(null); // Reference to editable content div
    const navigate = useNavigate();

    // States for toolbar formatting button active statuses
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

    // Predefined color options
    const colors = ['#000000', '#FF0000', '#00AA00', '#0000FF', '#FFA500', '#800080'];

    // Load note content when component mounts
    useEffect(() => {
        if (!noteId) return;
        const token = sessionStorage.getItem('auth_token');

        fetch(`${API_BASE}/api/v1/notes/${noteId}`, {
            method: 'GET',
            headers: {
                Authorization: `Bearer ${token}`,
            },
        })
            .then((response) => response.json())
            .then((data) => {
                setTitle(data.detail.title || 'Title');
                setContent(data.detail.content || '');
                if (contentRef.current) {
                    contentRef.current.innerHTML = data.detail.content || '';
                }
            })
            .catch((error) => console.error('Error fetching note:', error));
    }, [noteId]);

    // Save the note to backend
    const handleSave = () => {
        const token = sessionStorage.getItem('auth_token');

        fetch(`${API_BASE}/api/v1/notes/${noteId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify({
                title,
                content,
            }),
        })
            .then((response) => {
                if (!response.ok) throw new Error('Failed to save note');
                return response.json();
            })
            .then((data) => {
                navigate('/notes'); // Redirect after saving
                alert('Note saved successfully!');
            })
            .catch((error) => console.error('Save error:', error));
    };

    // Apply formatting to selected text
    const formatText = (command, value = null) => {
        document.execCommand(command, false, value);
        updateActiveStates(); // Update button states
        setContent(contentRef.current.innerHTML); // Save content to state
    };

    // Update active formatting button states
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

    // Change font color
    const handleColorChange = (e) => {
        const color = e.target.value;
        setCurrentColor(color);
        formatText('foreColor', color);
    };

    // Translate selected text
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
                    Authorization: `Bearer ${sessionStorage.getItem('auth_token')}`,
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
                throw new Error('Unexpected translation response format');
            }

            const range = sel.getRangeAt(0);
            range.deleteContents();
            range.insertNode(document.createTextNode(translatedText)); // Replace selection with translated text

            sel.removeAllRanges();
            setContent(contentRef.current.innerHTML); // Update content state
        } catch (err) {
            console.error(err);
            alert(err.message);
        }
    };

    // Attach event listeners to update formatting state on text selection change
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

    return (
        <>
            <header className="App-header">
                <img src={mkad} alt="mkad" />
                <div className="account">
                    <h3>{user_name}</h3>
                    <img src={account} alt="account" />
                </div>
            </header>
            <div className="edit_container">
                <input
                    type="text"
                    className="title_edit"
                    placeholder="Note Title"
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                />
                <div className="header">
                    <div className="edit_btns">
                        {/* Translation */}
                        <button className="edit_btn" type="button" onClick={handleTranslate}>
                            <img src={translateIcon} alt="translate" />
                        </button>
                        {/* Language selectors */}
                        <select value={sourceLang} onChange={(e) => setSourceLang(e.target.value)}>
                            <option value="auto">Auto</option>
                            <option value="en">English</option>
                            <option value="ru">Русский</option>
                        </select>
                        <select value={targetLang} onChange={(e) => setTargetLang(e.target.value)}>
                            <option value="ru">Русский</option>
                            <option value="en">English</option>
                        </select>
                        {/* Formatting buttons */}
                        <button
                            className={`edit_btn ${boldActive ? 'active' : ''}`}
                            type="button"
                            onClick={() => formatText('bold')}
                        >
                            <img src={boldIcon} alt="Bold" />
                        </button>
                        <button
                            className={`edit_btn ${italicActive ? 'active' : ''}`}
                            type="button"
                            onClick={() => formatText('italic')}
                        >
                            <img src={italicIcon} alt="Italic" />
                        </button>
                        <button
                            className={`edit_btn ${underlineActive ? 'active' : ''}`}
                            type="button"
                            onClick={() => formatText('underline')}
                        >
                            <img src={underlineIcon} alt="Underline" />
                        </button>
                        <button
                            className={`edit_btn ${strikeActive ? 'active' : ''}`}
                            type="button"
                            onClick={() => formatText('strikeThrough')}
                        >
                            <img src={strikethroughIcon} alt="Strikethrough" />
                        </button>
                        {/* Header formatting */}
                        <button
                            className={`edit_btn ${h1Active ? 'active' : ''}`}
                            type="button"
                            onClick={() => formatText('formatBlock', h1Active ? '<P>' : '<H1>')}
                        >
                            H1
                        </button>
                        <button
                            className={`edit_btn ${h2Active ? 'active' : ''}`}
                            type="button"
                            onClick={() => formatText('formatBlock', h2Active ? '<P>' : '<H2>')}
                        >
                            H2
                        </button>
                        <button
                            className={`edit_btn ${h3Active ? 'active' : ''}`}
                            type="button"
                            onClick={() => formatText('formatBlock', h3Active ? '<P>' : '<H3>')}
                        >
                            H3
                        </button>
                        {/* Color picker */}
                        <select
                            value={currentColor}
                            onChange={handleColorChange}
                            className="color-picker"
                        >
                            {colors.map((col) => (
                                <option key={col} value={col} style={{ backgroundColor: col, color: '#fff' }}>
                                    {col}
                                </option>
                            ))}
                        </select>
                    </div>
                    <button className="save-button" onClick={handleSave}>
                        Save
                    </button>
                </div>
                <div
                    className="edit-note-content"
                    contentEditable
                    ref={contentRef}
                    onInput={() => setContent(contentRef.current.innerHTML)}
                    suppressContentEditableWarning={true}
                    placeholder="Write your note here..."
                />
            </div>
        </>
    );
}

export default Edit;
