import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { API_BASE_URL } from '../config'; // 🔹 добавлено

interface Message {
  id: number;
  content: string;
  created_at: string;
  file_urls?: string;
  sender_id: number;
  chat_id: number;
}

const Chat: React.FC = () => {
  const { chatId } = useParams<{ chatId: string }>();
  const navigate = useNavigate();
  const [messages, setMessages] = useState<Message[]>([]);
  const [content, setContent] = useState('');
  const [files, setFiles] = useState<FileList | null>(null);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [editContent, setEditContent] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    if (!chatId) {
      setError('ID чата не найден');
      setIsLoading(false);
      return;
    }

    fetchMessages(chatId);
  }, [chatId, navigate]);

  const fetchMessages = async (id: string) => {
    try {
      setIsLoading(true);
      setError('');
      const response = await axios.get<Message[]>(`${API_BASE_URL}/messages/${id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      setMessages(response.data);
    } catch (error: any) {
      console.error('Error fetching messages:', error);
      if (error.response?.status === 401) {
        localStorage.removeItem('token');
        navigate('/login');
      } else if (error.response?.status === 404) {
        setError('Чат не найден');
      } else {
        setError('Ошибка загрузки сообщений');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!chatId) {
      setError('ID чата не найден');
      return;
    }

    if (!content.trim()) {
      setError('Введите сообщение');
      return;
    }

    const formData = new FormData();
    formData.append('content', content.trim());
    formData.append('chat_id', chatId);

    if (files) {
      Array.from(files).forEach((file) => formData.append('files', file));
    }

    try {
      const response = await axios.post<Message>(`${API_BASE_URL}/messages/`, formData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
          'Content-Type': 'multipart/form-data',
        },
      });

      setMessages([...messages, response.data]);
      setContent('');
      setFiles(null);
      setError('');

      const fileInput = document.querySelector('input[type="file"]') as HTMLInputElement;
      if (fileInput) fileInput.value = '';
    } catch (error: any) {
      console.error('Error sending message:', error);
      if (error.response?.data) {
        setError(`Ошибка отправки: ${JSON.stringify(error.response.data)}`);
      } else {
        setError('Ошибка отправки сообщения');
      }
    }
  };

  const handleEdit = async (id: number) => {
    try {
      const response = await axios.put<Message>(
        `${API_BASE_URL}/messages/${id}`,
        { content: editContent },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );
      setMessages(messages.map((m) => (m.id === id ? response.data : m)));
      setEditingId(null);
      setEditContent('');
    } catch (error: any) {
      console.error('Error editing:', error);
      setError('Ошибка редактирования сообщения');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await axios.delete(`${API_BASE_URL}/messages/${id}`, {
        headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
      });
      setMessages(messages.filter((m) => m.id !== id));
    } catch (error: any) {
      console.error('Error deleting:', error);
      setError('Ошибка удаления сообщения');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-100 p-4 flex items-center justify-center">
        <div className="text-xl">Загрузка сообщений...</div>
      </div>
    );
  }

  if (error && !chatId) {
    return (
      <div className="min-h-screen bg-gray-100 p-4 flex items-center justify-center">
        <div className="text-xl text-red-500">{error}</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100 p-4">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/chats')}
            className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded-lg transition-colors"
          >
            ← Назад к чатам
          </button>
          <div className="text-lg font-semibold">Чат {chatId}</div>
        </div>
        <button
          onClick={handleLogout}
          className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors"
        >
          Выйти
        </button>
      </div>

      {error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      <div className="bg-white p-4 rounded-lg shadow-md mb-4 max-h-[60vh] overflow-y-auto">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            {error ? error : 'Нет сообщений. Начните общение!'}
          </div>
        ) : (
          messages.map((msg) => (
            <div key={msg.id} className="mb-4 p-3 border-b border-gray-200 last:border-b-0">
              {editingId === msg.id ? (
                <div>
                  <input
                    value={editContent}
                    onChange={(e) => setEditContent(e.target.value)}
                    className="w-full px-3 py-2 border rounded-lg mb-2"
                    autoFocus
                  />
                  <div className="flex space-x-2">
                    <button
                      onClick={() => handleEdit(msg.id)}
                      className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded transition-colors"
                    >
                      Сохранить
                    </button>
                    <button
                      onClick={() => setEditingId(null)}
                      className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded transition-colors"
                    >
                      Отмена
                    </button>
                  </div>
                </div>
              ) : (
                <div>
                  <div className="flex justify-between items-start">
                    <p className="text-gray-800 flex-1">{msg.content}</p>
                    <div className="flex space-x-2 ml-4">
                      <button
                        onClick={() => {
                          setEditingId(msg.id);
                          setEditContent(msg.content);
                        }}
                        className="text-blue-500 hover:text-blue-700 text-sm transition-colors"
                      >
                        Редактировать
                      </button>
                      <button
                        onClick={() => handleDelete(msg.id)}
                        className="text-red-500 hover:text-red-700 text-sm transition-colors"
                      >
                        Удалить
                      </button>
                    </div>
                  </div>

                  {msg.file_urls && msg.file_urls !== '[]' && (
                    <div className="mt-2">
                      {JSON.parse(msg.file_urls).map((url: string, i: number) => (
                        <a
                          key={i}
                          href={`${API_BASE_URL}${url}`} // 🔹 заменено
                          target="_blank"
                          rel="noreferrer"
                          className="text-blue-500 hover:text-blue-700 inline-block mr-3 transition-colors"
                        >
                          📎 Файл {i + 1}
                        </a>
                      ))}
                    </div>
                  )}

                  <div className="text-xs text-gray-500 mt-1">
                    {new Date(msg.created_at).toLocaleString()}
                  </div>
                </div>
              )}
            </div>
          ))
        )}
      </div>

      <form onSubmit={handleSend} className="bg-white p-4 rounded-lg shadow-md">
        <div className="flex flex-col space-y-3">
          <input
            type="text"
            value={content}
            onChange={(e) => setContent(e.target.value)}
            placeholder="Введите сообщение..."
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            required
          />
          <div className="flex items-center space-x-3">
            <input
              type="file"
              multiple
              onChange={(e) => setFiles(e.target.files)}
              className="flex-1"
            />
            <button
              type="submit"
              className="bg-blue-500 hover:bg-blue-600 text-white px-6 py-2 rounded-lg transition-colors duration-200"
            >
              Отправить
            </button>
          </div>
        </div>
      </form>
    </div>
  );
};

export default Chat;
