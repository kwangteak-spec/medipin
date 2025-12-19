// src/components/Common/BottomNavBar.jsx (완전한 코드)

import React from 'react';
import { NavLink } from 'react-router-dom';
import './BottomNavBar.css';

const BottomNavBar = () => {
    // 🚨 1. navItems 배열에 실제 경로와 아이콘 정의를 추가합니다.
    const navItems = [
        { path: '/search', icon: '🔍', label: 'Search' },
        { path: '/map', icon: '📍', label: 'Map' },
        { path: '/calendar', icon: '📅', label: 'Calendar' },
        { path: '/mypage', icon: '👤', label: 'My page' },
    ];

    return (
        <nav className="bottom-nav">
            {navItems.map(item => (
                <NavLink 
                    key={item.path}
                    to={item.path} 
                    // 현재 경로에 따라 활성 스타일 적용
                    className={({ isActive }) => 
                        isActive ? "nav-item active" : "nav-item"
                    }
                >
                    <span className="nav-icon">{item.icon}</span>
                    <span className="nav-label">{item.label}</span>
                </NavLink>
            ))}
            
            {/* 🚨 2. 중앙 채팅 버튼 wrapper를 추가합니다. */}
            <div className="chat-button-wrapper">
                <button className="chat-button">💬</button> 
            </div>
        </nav>
    );
};

export default BottomNavBar;