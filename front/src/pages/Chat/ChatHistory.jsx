import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { API_BASE_URL } from "../../api/config";
import bearIcon from "../../assets/medipin_bear_icon.png";
import "./style.css";

const formatTime = (dateStr) => {
    if (!dateStr) return "";
    const now = new Date();
    const past = new Date(dateStr);
    const diffMs = now - past;
    const diffSec = Math.floor(diffMs / 1000);
    const diffMin = Math.floor(diffSec / 60);
    const diffHr = Math.floor(diffMin / 60);
    const diffDay = Math.floor(diffHr / 24);

    if (diffMin < 1) return "now";
    if (diffMin < 60) return `${diffMin} min`;
    if (diffHr < 24) return `${diffHr}h`;
    if (diffDay <= 7) return `${diffDay}day`;

    return `${past.getMonth() + 1}. ${past.getDate()}`;
};

const formatUnreadCount = (count) => {
    if (count >= 10) return "10+";
    return count > 0 ? count.toString() : "";
};

export const ChatHistory = () => {
    const navigate = useNavigate();
    const [history, setHistory] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchHistory = async () => {
        const token = localStorage.getItem("authToken");
        if (!token) {
            setLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/chatbot/history`, {
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });
            if (response.ok) {
                const data = await response.json();
                setHistory(data);
            } else {
                setError("Failed to load history (404/500)");
            }
        } catch (err) {
            setError("Error fetching history");
        } finally {
            setLoading(false);
        }
    };

    const handleDelete = async (e, historyId) => {
        e.stopPropagation(); // Prevent navigation to chat
        if (!window.confirm("이 대화 내역을 삭제하시겠습니까?")) return;

        const token = localStorage.getItem("authToken");
        if (!token) return;

        try {
            const response = await fetch(`${API_BASE_URL}/chatbot/history/${historyId}`, {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.ok) {
                // Remove from local state
                setHistory(prev => prev.filter(item => item.id !== historyId));
            } else {
                alert("삭제에 실패했습니다.");
            }
        } catch (err) {
            console.error("Delete error:", err);
            alert("삭제 중 오류가 발생했습니다.");
        }
    };

    useEffect(() => {
        fetchHistory();
    }, []);

    if (loading && history.length === 0) {
        return <div className="loading-history">Loading history...</div>;
    }

    // If there's an error or no history, handle empty state
    const hasHistory = history && history.length > 0;

    const displayHistory = hasHistory ? history.map((item, index) => ({
        id: item.id || index,
        message: item.message,
        time: formatTime(item.created_at),
        unread: !item.is_read && item.sender === 'bot' ? 1 : 0,
        sender: item.sender
    })) : [
        { id: 1, message: "아직 대화 내역이 없습니다. 메시지를 보내보세요!", time: "now", unread: 0, sender: 'bot' }
    ];


    return (
        <div className="history-container">
            <div className="history-list">
                {displayHistory.map((item) => (
                    <div
                        key={item.id}
                        className={`history-item ${item.sender}`}
                        onClick={() => navigate("/chat?history=true")}
                        style={{ cursor: "pointer" }}
                    >
                        <div className="avatar-section">
                            {item.sender === 'bot' && (
                                <img src={bearIcon} alt="Avatar" className="bear-avatar" />
                            )}
                        </div>
                        <div className="info-section">
                            <div className="info-top">
                                <div className="item-meta">
                                    <button
                                        className="delete-button"
                                        onClick={(e) => handleDelete(e, item.id)}
                                    >
                                        ✕
                                    </button>
                                    <span className="item-time">{item.time}</span>
                                </div>
                            </div>
                            <div className="info-bottom">
                                <div className="item-message">{item.message}</div>
                                {item.unread > 0 && (
                                    <div className="unread-bubble">{formatUnreadCount(item.unread)}</div>
                                )}
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
};
