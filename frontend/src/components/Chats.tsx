import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config'; // 🔹 добавляем импорт

interface Chat {
  id: number;
  name: string;
}

interface User {
  id: number;
  username: string;
}

const Chats: React.FC = () => {
  const [chats, setChats] = useState<Chat[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [recipientId, setRecipientId] = useState<number>(0);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    fetchChats();
    fetchUsers();
  }, [navigate]);

  const fetchChats = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No token available');
      // 🔹 заменено localhost → API_BASE_URL
      const response = await axios.get<Chat[]>(`${API_BASE_URL}/chats/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      console.log('Fetched chats:', response.data);
      setChats(response.data);
    } catch (error) {
      console.error('Error fetching chats:', error);
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      }
    }
  };

  const fetchUsers = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No token available');
      // 🔹 заменено localhost → API_BASE_URL
      const response = await axios.get<User[]>(`${API_BASE_URL}/users/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setUsers(response.data);
    } catch (error) {
      console.error('Error fetching users:', error);
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      }
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  const handleCreateChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!recipientId) return;
    try {
      const token = localStorage.getItem('token');
      if (!token) throw new Error('No token available');
      // 🔹 заменено localhost → API_BASE_URL
      const response = await axios.post<Chat>(
        `${API_BASE_URL}/chats/`,
        { name: '', recipient_id: recipientId },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      const newChat = response.data;
      setChats([...chats, newChat]);
      setRecipientId(0);
      navigate(`/chat/${newChat.id}`);
    } catch (error) {
      console.error('Error creating chat:', error);
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Чаты</h2>
        <button onClick={handleLogout} className="bg-red-500 text-white px-4 py-2 rounded-lg">
          Выйти
        </button>
      </div>

      <form onSubmit={handleCreateChat} className="mb-4">
        <div className="flex space-x-2">
          <select
            value={recipientId}
            onChange={(e) => setRecipientId(Number(e.target.value))}
            className="flex-1 px-3 py-2 border rounded-lg"
            required
          >
            <option value={0}>Выбери пользователя</option>
            {users.map((user) => (
              <option key={user.id} value={user.id}>{user.username}</option>
            ))}
          </select>
          <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded-lg">
            Создать чат
          </button>
        </div>
      </form>

      <div className="bg-white rounded-lg shadow-md">
        {chats.length === 0 ? (
          <div className="text-center text-gray-500 py-8">Нет чатов. Создайте первый чат!</div>
        ) : (
          <ul>
            {chats.map((chat) => (
              <li key={chat.id} className="border-b border-gray-200 last:border-b-0">
                <button
                  onClick={() => navigate(`/chat/${chat.id}`)}
                  className="w-full text-left px-4 py-3 hover:bg-gray-50 transition-colors"
                >
                  <div className="font-medium">{chat.name || `Чат ${chat.id}`}</div>
                  <div className="text-sm text-gray-500">ID: {chat.id}</div>
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  );
};

export default Chats;
