import React from "react";
import { useParams, useNavigate, useLocation } from "react-router-dom";
import { HomeBar } from "../../components/HomeBar/HomeBar";
import preIcon from "../Search_detail/pre_icon.svg"; // 뒤로가기 아이콘 재사용
import "./style.css";

const MapRInfo = () => {
    const { name } = useParams(); // URL 파라미터
    const navigate = useNavigate();
    const location = useLocation();

    const place = location.state || {
        name: name || "정보 없음",
        address: "주소 정보가 없습니다.",
        phone: "전화번호 정보가 없습니다.",
        type: "unknown",
    };

    /* 영업 상태 로직 */
    const getStatusText = (data) => {
        // 데이터가 없으면 공백
        if (!data.dutyTimeStart || !data.dutyTimeClose) return "";

        const now = new Date();
        const currentHour = now.getHours();
        const currentMin = now.getMinutes();
        const currentTime = currentHour * 100 + currentMin; // HHMM 형식

        // 예시 데이터 파싱 (실제 데이터 형식에 따라 수정 필요)
        // 여기서는 데이터가 없으므로 넘어갑니다.
        // 만약 future implementation에서 data.dutyTimeStart = "0900", data.dutyTimeClose = "1800" 등으로 온다면:
        /*
        const start = parseInt(data.dutyTimeStart);
        const close = parseInt(data.dutyTimeClose);
        const breakStart = data.breakStart ? parseInt(data.breakStart) : null;
        const breakEnd = data.breakEnd ? parseInt(data.breakEnd) : null;
        
        // 휴게 시간 체크
        if (breakStart && breakEnd) {
            if (currentTime >= breakStart && currentTime < breakEnd) return "휴게시간";
            if (currentTime < breakStart && breakStart - currentTime <= 30) return "곧 휴게시간";
        }

        // 영업 종료 체크
        if (currentTime >= start && currentTime < close) {
            if (close - currentTime <= 30) return "곧 영업종료";
            return "영업중";
        }
        return "영업종료";
        */

        return "";
    };

    return (
        <div className="map-r-info">
            {/* 상단 보라색 배경 영역 */}
            <div className="top-header">
                <div className="header-nav">
                    <div className="back-btn" onClick={() => navigate(-1)}>
                        <img src={preIcon} alt="Back" />
                    </div>
                    <div className="header-title">{place.name}</div>
                </div>
            </div>

            {/* 하단 상세 정보 카드 (사진 포함) */}
            <div className="info-card">
                {/* 사진 영역 */}
                <div className="photo-area">
                    <div className="main-image-placeholder">
                        <svg
                            width="60"
                            height="60"
                            viewBox="0 0 24 24"
                            fill="none"
                            xmlns="http://www.w3.org/2000/svg"
                        >
                            <path
                                d="M21 19V5C21 3.9 20.1 3 19 3H5C3.9 3 3 3.9 3 5V19C3 20.1 3.9 21 5 21H19C20.1 21 21 20.1 21 19ZM8.5 13.5L11 16.51L14.5 12L19 18H5L8.5 13.5Z"
                                fill="#D1D5DB"
                            />
                        </svg>
                    </div>
                </div>
                <div className="info-header">
                    <h2>{place.name}</h2>
                </div>

                <div className="info-list">
                    {/* 1. 주소 */}
                    <div className="info-item">
                        <div className="icon-wrapper">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"></path><circle cx="12" cy="10" r="3"></circle></svg>
                        </div>
                        <div className="info-content">{place.address}</div>
                    </div>

                    {/* 2. 자세한 안내사항 (데이터 없으면 공백) */}
                    <div className="info-item">
                        <div className="icon-wrapper">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 18l6-6-6-6"></path></svg>
                        </div>
                        <div className="info-content text-gray">
                            {place.instructions || ""}
                        </div>
                    </div>

                    {/* 3. 전화번호 */}
                    <div className="info-item">
                        <div className="icon-wrapper">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6 19.79 19.79 0 0 1-3.07-8.67A2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72 12.84 12.84 0 0 0 .7 2.81 2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45 12.84 12.84 0 0 0 2.81.7A2 2 0 0 1 22 16.92z"></path></svg>
                        </div>
                        <div className="info-content">{place.phone || place.tel}</div>
                    </div>

                    {/* 4. 영업시간 */}
                    <div className="info-item">
                        <div className="icon-wrapper">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="12 6 12 12 16 14"></polyline></svg>
                        </div>
                        <div className="info-content">
                            {/* 영업시간 로직 적용 (데이터 없으면 공백) */}
                            {getStatusText(place)}
                        </div>
                    </div>

                    {/* 5. 해당 기관 사이트 */}
                    <div className="info-item">
                        <div className="icon-wrapper">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#333" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="2" y1="12" x2="22" y2="12"></line><path d="M12 2a15.3 15.3 0 0 1 4 10 15.3 15.3 0 0 1-4 10 15.3 15.3 0 0 1-4-10 15.3 15.3 0 0 1 4-10z"></path></svg>
                        </div>
                        <div className="info-content">
                            {place.homepage ? (
                                <a href={place.homepage} target="_blank" rel="noopener noreferrer" style={{ color: '#000', textDecoration: 'none' }}>
                                    {place.homepage}
                                </a>
                            ) : ""}
                        </div>
                    </div>

                    {/* 특이사항 (맨 아래 회색) */}
                    <div className="extra-info">
                        {place.note || ""}
                    </div>
                </div>
            </div>

            {/* 하단 네비게이션 */}
            <div className="bottom-nav-container">
                <HomeBar />
            </div>
        </div>
    );
};

export default MapRInfo;
