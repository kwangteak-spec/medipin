import React, { useRef, useState, useEffect } from "react";
import { useNavigate } from "react-router-dom"; // 🚨 추가
import ambulanceIcon from "../../assets/ambulance.svg"; // ✅ Import ambulance icon
import "./style.css";

const SHEET = {
    CLOSED: "CLOSED",
    MIN: "MIN",
    FULL: "FULL",
};

const MapList = ({ sheetState, setSheetState, places = [], selectedPlace, setSelectedPlace }) => {
    const sheetRef = useRef(null);
    const startY = useRef(0);
    const currentY = useRef(0);
    const [dragging, setDragging] = useState(false);
    const navigate = useNavigate(); // 🚨 추가

    /* 상태별 위치 계산 */
    const getTranslateY = () => {
        const vh = window.innerHeight;
        // 하단 네비게이션(약 80px) 고려
        if (sheetState === SHEET.CLOSED) return vh; // 아예 보이지 않게 숨김
        if (sheetState === SHEET.MIN) return vh - 400; // 살짝 내려서 적절한 높이 유지
        if (sheetState === SHEET.FULL) return 100; // 거의 다 보임
        return vh;
    };

    /* 상태 변경 시 위치 반영 */
    useEffect(() => {
        if (!sheetRef.current) return;
        sheetRef.current.style.transform = `translate(-50%, ${getTranslateY()}px)`;
    }, [sheetState]);

    /* 드래그 시작 */
    const onStart = (e) => {
        setDragging(true);
        const y = e.touches ? e.touches[0].clientY : e.clientY;
        startY.current = y;
        currentY.current = y;
    };

    /* 드래그 중 및 종료 핸들러를 useEffect로 관리 (글로벌 리스너) */
    useEffect(() => {
        if (!dragging) return;

        const handleMove = (e) => {
            const clientY = e.touches ? e.touches[0].clientY : e.clientY;
            currentY.current = clientY;
            const delta = clientY - startY.current;

            if (sheetRef.current) {
                // 실시간 드래그 반영 (1:1 추적)
                sheetRef.current.style.transform = `translate(-50%, ${getTranslateY() + delta}px)`;
            }
        };

        const handleEnd = () => {
            setDragging(false);
            const delta = currentY.current - startY.current;

            // 스냅 로직
            if (delta < -80) { // 위로 충분히 올림
                if (sheetState === SHEET.MIN) setSheetState(SHEET.FULL);
            } else if (delta > 80) { // 아래로 충분히 내림
                if (sheetState === SHEET.FULL) setSheetState(SHEET.MIN);
                else setSheetState(SHEET.CLOSED);
            } else {
                // 원복
                if (sheetRef.current) {
                    sheetRef.current.style.transform = `translate(-50%, ${getTranslateY()}px)`;
                }
            }
        };

        window.addEventListener("mousemove", handleMove);
        window.addEventListener("mouseup", handleEnd);
        window.addEventListener("touchmove", handleMove, { passive: false });
        window.addEventListener("touchend", handleEnd);

        return () => {
            window.removeEventListener("mousemove", handleMove);
            window.removeEventListener("mouseup", handleEnd);
            window.removeEventListener("touchmove", handleMove);
            window.removeEventListener("touchend", handleEnd);
        };
    }, [dragging, sheetState]);

    const handleCardClick = (place) => {
        // 상세 페이지 이동 대신, 내부 상태 변경으로 Detail View 전환
        setSelectedPlace(place);
        // 바텀시트가 닫혀있거나 최소화 상태면 올리기 (UX)
        if (sheetState === SHEET.CLOSED) setSheetState(SHEET.MIN);
    };

    const handleBackToList = () => {
        setSelectedPlace(null);
    };

    return (
        <div ref={sheetRef} className="map-list" style={{ transition: dragging ? 'none' : 'transform 0.3s ease-out' }}>
            {/* 드래그 핸들 */}
            <div
                className="handle"
                onMouseDown={onStart}
                onTouchStart={onStart}
            >
                <div className="handle-bar" />
            </div>

            {/* 리스트 컨텐츠 or 상세 컨텐츠 */}
            <div className="list-content">
                {selectedPlace ? (
                    // --- 상세 뷰 ---
                    <div className="detail-view">
                        <button className="back-btn" onClick={handleBackToList}>
                            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                                <path d="M15 18L9 12L15 6" stroke="#111" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round" />
                            </svg>
                        </button>
                        <div className="detail-image-wrapper">
                            <img
                                src={selectedPlace.type === 'hospital'
                                    ? "https://postfiles.pstatic.net/MjAyNTEyMDlfODYg/MDAxNzY1MjU4NTgxMTE3.OR1zSpBxdcgRJ3VwdV_GHl9qojPdx9JQmyy2Bz-XQ8og.aSJDea3drP1B7zcwZc-V02F42kqp3XR9BR7liqI8h40g.PNG/hospital.png?type=w966"
                                    : selectedPlace.type === 'emergency'
                                        ? ambulanceIcon
                                        : selectedPlace.type === 'convenience'
                                            ? "https://postfiles.pstatic.net/MjAyNTEyMDlfMjUx/MDAxNzY1MjU4NTgxMTE3.Ruq6sQhusMsEEGY4E5bDbIDr5CdgsO3FM9urY0_iykwg.dm7HDIzMQOfLV3zzyl80gPdXdW54XNJWjDEVKuCg6_Qg.PNG/conveni.png?type=w966"
                                            : "https://postfiles.pstatic.net/MjAyNTEyMDlfMjY1/MDAxNzY1MjU4ODI0ODI4._p_9MD5vjkfIGL_iIUBCSVHhx5JTAG9wqhRkxrmuei0g.Mo5O6ZABPabGYjuAScmOmCcab_BYlKUwcf-SjEnWVk0g.PNG/pill-removebg-preview.png?type=w966"
                                }
                                alt={selectedPlace.name}
                                className="detail-image"
                            />
                        </div>
                        <div className="detail-info">
                            <h2 className="detail-name">{selectedPlace.name}</h2>
                            <span className="detail-badge">영업중</span>
                            <div className="detail-row">
                                <span className="label">주소</span>
                                <span>{selectedPlace.address}</span>
                            </div>
                            <div className="detail-row">
                                <span className="label">전화</span>
                                <span>{selectedPlace.tel || selectedPlace.phone || "정보 없음"}</span>
                            </div>
                            {selectedPlace.homepage && (
                                <div className="detail-row">
                                    <span className="label">홈페이지</span>
                                    <a href={selectedPlace.homepage} target="_blank" rel="noreferrer" style={{ color: '#9F63FF' }}>
                                        방문하기
                                    </a>
                                </div>
                            )}
                        </div>
                    </div>
                ) : (
                    // --- 리스트 뷰 ---
                    places.length === 0 ? (
                        <div style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                            검색 결과가 없습니다.
                        </div>
                    ) : (
                        places.map((place, index) => (
                            <div
                                key={index}
                                className="place-card"
                                onClick={() => handleCardClick(place)}
                            >
                                <div className="place-image-wrapper">
                                    <img
                                        src={place.type === 'hospital'
                                            ? "https://postfiles.pstatic.net/MjAyNTEyMDlfODYg/MDAxNzY1MjU4NTgxMTE3.OR1zSpBxdcgRJ3VwdV_GHl9qojPdx9JQmyy2Bz-XQ8og.aSJDea3drP1B7zcwZc-V02F42kqp3XR9BR7liqI8h40g.PNG/hospital.png?type=w966"
                                            : place.type === 'emergency'
                                                ? ambulanceIcon
                                                : place.type === 'convenience'
                                                    ? "https://postfiles.pstatic.net/MjAyNTEyMDlfMjUx/MDAxNzY1MjU4NTgxMTE3.Ruq6sQhusMsEEGY4E5bDbIDr5CdgsO3FM9urY0_iykwg.dm7HDIzMQOfLV3zzyl80gPdXdW54XNJWjDEVKuCg6_Qg.PNG/conveni.png?type=w966"
                                                    : "https://postfiles.pstatic.net/MjAyNTEyMDlfMjY1/MDAxNzY1MjU4ODI0ODI4._p_9MD5vjkfIGL_iIUBCSVHhx5JTAG9wqhRkxrmuei0g.Mo5O6ZABPabGYjuAScmOmCcab_BYlKUwcf-SjEnWVk0g.PNG/pill-removebg-preview.png?type=w966"
                                        }
                                        alt={place.name}
                                        className="place-image"
                                    />
                                </div>
                                <div className="place-info">
                                    <div className="place-header">
                                        <span className="place-name">{place.name}</span>
                                    </div>
                                    <div className="place-status active">영업중</div>
                                    <div className="place-address">{place.address}</div>
                                    <div className="place-phone">{place.tel || place.phone || "정보 없음"}</div>
                                </div>
                            </div>
                        ))
                    )
                )}
            </div>
        </div>
    );
};

export default MapList;
