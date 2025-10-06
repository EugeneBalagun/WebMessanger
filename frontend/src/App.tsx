import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Chats from './components/Chats';
import Chat from './components/Chat';
import './index.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<Navigate to="/chats" replace />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/chats" element={<Chats />} />
          <Route path="/chat/:chatId" element={<Chat />} /> {/* ИЗМЕНИЛ ПУТЬ */}
        </Routes>
      </div>
    </Router>
  );
}

export default App;