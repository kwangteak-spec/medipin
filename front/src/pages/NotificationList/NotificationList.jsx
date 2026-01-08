import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { formatDistanceToNow } from "date-fns";
import bearIcon from "../../assets/medipin_bear_icon.png";
import { API_BASE_URL } from "../../api/config";
import { HomeBar } from "../../components/HomeBar/HomeBar";
import { BackIcon } from "../../components/Icons";
import { useAlarm } from "../../context/AlarmContext";
import "./style.css";

const NotificationList = () => {
    const navigate = useNavigate();
    const { toggleOverlay } = useAlarm();
    const [notifications, setNotifications] = useState([]);
    const [loading, setLoading] = useState(true);
    const storedUserId = localStorage.getItem("userId");
    const USER_ID = storedUserId ? parseInt(storedUserId) : 1;

    useEffect(() => {
        fetchNotifications();
    }, []);

    const fetchNotifications = async () => {
        const token = localStorage.getItem("authToken");
        if (!token) return;

        setLoading(true);
        try {
            // 알림 히스토리 API 호출
            const res = await fetch(`${API_BASE_URL}/alarms/history?user_id=${USER_ID}`, {
                headers: {
                    "Accept": "application/json",
                    "Authorization": `Bearer ${token}`
                }
            });
            if (res.ok) {
                const data = await res.json();
                setNotifications(data);
            } else if (res.status === 401) {
                console.warn("Unauthorized notification fetch");
                // navigate('/login'); // 필요 시 로그인 페이지로 이동
            }
        } catch (error) {
            console.error(error);
        } finally {
            setLoading(false);
        }
    };

    // Icons integrated from centralized component

    const getTimeAgo = (item) => {
        if (item.alarm_time) {
            return formatDistanceToNow(new Date(item.alarm_time), { addSuffix: true });
        }
        return "";
    };

    const handleItemClick = (item) => {
        if (!item.alarm_time) return;
        const dateStr = item.alarm_time.split('T')[0];
        navigate(`/calendar?date=${dateStr}`);
    };

    return (
        <div className="notification-page">
            {/* 헤더 */}
            <div className="mypage-header">
                <div style={{ width: 56, display: 'flex', alignItems: 'center', justifyContent: 'flex-start' }}>
                    <button onClick={() => navigate(-1)} className="mypage-back-btn">
                        <BackIcon />
                    </button>
                </div>
                <div className="header-title">Notification List</div>
                <div className="icon-wrapper" onClick={toggleOverlay}>
                    <div className="icon-alarm" />
                </div>
            </div>

            <div className="content-scrollable">
                <div className="notification-list-container">
                    {loading ? (
                        <div className="loading">로딩 중...</div>
                    ) : notifications.length === 0 ? (
                        <div className="no-data">알림 기록이 없습니다.</div>
                    ) : (
                        <div className="noti-list">
                            {notifications.map((item, index) => {
                                const isCompleted = item.is_taken || item.is_read;
                                return (
                                    <div
                                        key={item.id || index}
                                        className={`noti-item ${isCompleted ? 'completed' : ''}`}
                                        onClick={() => handleItemClick(item)}
                                    >
                                        <div className="bear-icon">
                                            <img src={bearIcon} alt="bear" style={{ filter: isCompleted ? 'grayscale(100%)' : 'none' }} />
                                        </div>
                                        <div className="noti-info">
                                            <div className="noti-title">MediPin</div>
                                            <div className="noti-desc">
                                                {item.pill_name ? `${item.pill_name} 복용 시간입니다.` : item.message}
                                                <br />
                                                <span className="status-label" style={{ color: isCompleted ? '#aaa' : '#9F63FF' }}>
                                                    {isCompleted ? "확인 완료" : "미복용"}
                                                </span>
                                            </div>
                                        </div>
                                        <div className="noti-time">
                                            {getTimeAgo(item)}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </div>
                {/* Padding for bottom nav */}
                <div style={{ height: 80 }}></div>
            </div>

            {/* 하단 네비게이션 */}
            <div className="bottom-nav-container">
                <HomeBar />
                <div className="bottom-filler"></div>
            </div>
        </div>
    );
};

export default NotificationList;
