import React, { useState, useEffect } from 'react';
import './style.css';
import '../../style/style.css';
import mkad from '../../assets/icon/MKAD.svg'
import deleteIcon from '../../assets/icon/delete.svg'
import plus from '../../assets/icon/white_plus.svg'
import account from '../../assets/illustration/account.svg'
import background1 from '../../assets/illustration/background1.png'
import background2 from '../../assets/illustration/background2.png'
import background3 from '../../assets/illustration/background3.png'
import background4 from '../../assets/illustration/background4.png'
import background5 from '../../assets/illustration/background5.png'
import {useNavigate} from "react-router-dom";

// Get the API base URL from environment variables
const API_BASE = process.env.REACT_APP_API_BASE_URL;
// Array of background images to cycle through notes
const backgroundImages = [background1, background2, background3, background4, background5];

function Notes() {
    // Get user name from session storage (parsed from JSON)
    const [user_name, setUser_name] = useState(JSON.parse(sessionStorage.getItem('user')).name);
    const navigate = useNavigate();
    const [notes, setNotes] = useState([]);

    // Navigate to the create note page
    const handleCreate = () => {
        navigate('/create');
    }

    // Navigate to the edit page with noteId passed via state
    const handleEdit = (noteId) => {
        navigate('/edit', { state: { noteId } });
    }

    // Handle note deletion
    const handleDelete = (noteId, e) => {
        e.stopPropagation(); // Prevent triggering the /edit navigation
        const token = sessionStorage.getItem('auth_token');
        if (!token) {
            alert("No authorization token.");
            return;
        }

        // Send DELETE request to remove the note
        fetch(`${API_BASE}/api/v1/notes/${noteId}`, {
            method: 'DELETE',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error deleting note');
                }
                // Remove the deleted note from state
                setNotes(prevNotes => prevNotes.filter(note => note.note_id !== noteId));
            })
            .catch(error => {
                console.error("Error deleting:", error);
                alert("Failed to delete the note.");
            });
    };

    // Fetch notes when component mounts
    useEffect(() => {
        const token = sessionStorage.getItem('auth_token');
        if (!token) {
            alert("No authorization token.");
            return;
        }

        // Send GET request to fetch notes
        fetch(`${API_BASE}/api/v1/notes/`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error fetching notes');
                }
                return response.json();
            })
            .then(data => {
                setNotes(data.detail);
                console.log(notes); // Debugging: log current notes
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Failed to load notes.");
            });
    }, []);

    return (
        <>
            {/* App header with logo and user account */}
            <header className="App-header">
                <img src={mkad} alt="mkad" />
                <div className="account">
                    <h3>{user_name}</h3>
                    <img src={account} alt="account" />
                </div>
            </header>
            <div className="notes_container">
                {/* Button to create a new note */}
                <button className="create_note_btn" onClick={handleCreate}>
                    <img src={plus} alt="plus" />
                    <h3 className="semiBold">Create note</h3>
                </button>
                <div className="notes_wrapper">
                    {/* List of notes */}
                    {notes.map((note, index) => (
                        <button className="note_block" onClick={() => handleEdit(note.note_id)} key={note.note_id || index}>
                            <img src={backgroundImages[index % backgroundImages.length]} alt="background"/>
                            <div className="note_block_text">
                                <h3 className="medium flex_start">{note.title}</h3>
                                <div className="note_block_name">
                                    <h4>Opened: {new Date(note.updated_at).toLocaleDateString()}</h4>
                                    {/* Delete button inside each note */}
                                    <button className="note_delete" onClick={(e) => handleDelete(note.note_id, e)}>
                                        <img src={deleteIcon} alt="delete" />
                                    </button>
                                </div>
                            </div>
                        </button>
                    ))}
                </div>
            </div>
        </>
    )
}

export default Notes;
