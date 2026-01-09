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

    const handleDelete = async (e, conversationId) => {
        e.stopPropagation(); // Prevent navigation
        if (!window.confirm("이 대화 내역을 전체 삭제하시겠습니까?")) return;

        const token = localStorage.getItem("authToken");
        if (!token) return;

        try {
            const response = await fetch(`${API_BASE_URL}/chatbot/conversation/${conversationId}`, {
                method: "DELETE",
                headers: {
                    Authorization: `Bearer ${token}`,
                },
            });

            if (response.ok) {
                // Remove all messages with this conversationId from local state
                setHistory(prev => prev.filter(item => {
                    const cid = item.conversation_id || 'default';
                    return cid !== conversationId;
                }));
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

    const displayHistory = [];
    if (hasHistory) {
        // Group messages by conversation_id
        const groups = {};
        history.forEach(item => {
            const cid = item.conversation_id || 'default';
            if (!groups[cid]) {
                groups[cid] = {
                    id: cid,
                    name: "메디핀 AI",
                    messages: [],
                    latest_at: item.created_at
                };
            }
            groups[cid].messages.push(item);
            if (new Date(item.created_at) > new Date(groups[cid].latest_at)) {
                groups[cid].latest_at = item.created_at;
            }
        });

        // Convert groups to display format and sort by latest
        Object.values(groups).sort((a, b) => new Date(b.latest_at) - new Date(a.latest_at)).forEach(group => {
            const latestMsg = group.messages.sort((a, b) => new Date(b.created_at) - new Date(a.created_at))[0];
            const unreadCount = group.messages.reduce((sum, m) => sum + (!m.is_read && m.sender === 'bot' ? 1 : 0), 0);

            displayHistory.push({
                id: group.id,
                name: group.name,
                message: latestMsg.message,
                time: formatTime(latestMsg.created_at),
                unread: unreadCount,
                sender: 'bot'
            });
        });
    } else {
        displayHistory.push({
            id: 'empty',
            name: "메디핀 AI",
            message: "아직 대화 내역이 없습니다. 메시지를 보내보세요!",
            time: "now",
            unread: 0,
            sender: 'bot'
        });
    }


    return (
        <div className="history-container">
            {!hasHistory ? (
                <div className="empty-history">
                    아직 대화 내역이 없습니다.<br /> 메세지를 입력해주세요
                </div>
            ) : (
                <div className="history-list">
                    {displayHistory.map((item) => (
                        <div
                            key={item.id}
                            className={`history-item bot`}
                            onClick={() => navigate(`/chat?history=true&cid=${item.id}`)}
                            style={{ cursor: "pointer" }}
                        >
                            <div className="avatar-section">
                                <img src={bearIcon} alt="Avatar" className="bear-avatar" />
                            </div>
                            <div className="info-section">
                                <div className="info-top">
                                    <span className="item-name">{item.name}</span>
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
            )}
        </div>
    );
};
