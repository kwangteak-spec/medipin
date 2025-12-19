import React, { useState, useEffect, useRef } from "react";
import { format, addMonths, subMonths, startOfMonth, endOfMonth, startOfWeek, endOfWeek, isSameMonth, isSameDay, parseISO } from "date-fns";
import { HomeBar } from "../../components/HomeBar/HomeBar";
/* 아이콘들 */
import preIcon from "../Search_detail/pre_icon.svg";
import "./style.css";

const Calendar = () => {
    // 날짜 상태
    const [currentMonth, setCurrentMonth] = useState(new Date());
    const [selectedDate, setSelectedDate] = useState(new Date());

    // 데이터 상태
    const [schedules, setSchedules] = useState([]);
    const [loading, setLoading] = useState(false);

    // 모드 상태
    const [isAddMode, setIsAddMode] = useState(false);

    // 드래그 관련 상태 (List Sheet)
    const [sheetHeight, setSheetHeight] = useState(50); // vh 단위
    const listSheetRef = useRef(null);
    const dragStartY = useRef(0);
    const dragStartHeight = useRef(0);

    // 드래그 관련 상태 (Add Sheet)
    const [addSheetHeight, setAddSheetHeight] = useState(0);
    const addSheetRef = useRef(null);
    const addDragStartY = useRef(0);
    const addDragStartHeight = useRef(0);

    // 폼 상태
    const [formData, setFormData] = useState({
        pill_name: "",
        dose: "",
        date: "",
        start_time: "",
        end_time: "",
        timing: "",
        memo: "",
    });

    const API_URL = "http://127.0.0.1:8000/medication";
    const USER_ID = 1; // 임시 사용자 ID (로그인 연동 시 변경 필요)

    // --- 데이터 패칭 ---
    useEffect(() => {
        fetchSchedules();
    }, [currentMonth]);

    const fetchSchedules = async () => {
        setLoading(true);
        try {
            const year = currentMonth.getFullYear();
            const month = currentMonth.getMonth() + 1;
            // API에서 월별 필터링 지원한다고 가정 (router구현됨)
            const res = await fetch(`${API_URL}/schedule?user_id=${USER_ID}&year=${year}&month=${month}`);
            if (res.ok) {
                const data = await res.json();
                setSchedules(data);
            } else {
                console.error("Failed to fetch schedules");
            }
        } catch (error) {
            console.error("Error fetching schedules:", error);
        } finally {
            setLoading(false);
        }
    };

    // --- 이벤트 핸들러 ---

    const handleDateClick = (day) => {
        setSelectedDate(day);
        // "캘린더 부분 클릭하면 리스트가 내려가도록" -> 최소 높이로 축소
        setSheetHeight(30);
        // 폼 초기화 (선택된 날짜로)
        setFormData(prev => ({
            ...prev,
            date: format(day, 'yyyy-MM-dd')
        }));
    };

    const handleFormChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleSubmit = async () => {
        if (!formData.pill_name) {
            alert("Pill name is required");
            return;
        }

        // Schema: user_id, pill_name, dose, date, ...
        // UI Start time / End time -> timing 필드에 병합 저장 (예: "10:00-12:00")
        // 또는 start_date/end_date는 기간(Date)일 수 있음. 여기서는 date(하루) 기준이므로
        // UI의 Start/End time은 시간 문자열로 간주하여 timing이나 memo에 넣거나,
        // user schema의 timing에 넣는 것이 적절해 보임.
        // *User Schema*: timing (String).

        let timingStr = formData.timing;
        if (formData.start_time && formData.end_time) {
            timingStr = `${formData.start_time}-${formData.end_time}`;
        } else if (formData.start_time) {
            timingStr = formData.start_time;
        }

        const payload = {
            user_id: USER_ID,
            pill_name: formData.pill_name,
            dose: formData.dose,
            date: formData.date || format(selectedDate, 'yyyy-MM-dd'),
            start_date: formData.date || format(selectedDate, 'yyyy-MM-dd'), // Start/End date to same day for single event
            end_date: formData.date || format(selectedDate, 'yyyy-MM-dd'),
            timing: timingStr, // 시간 정보
            meal_relation: null,
            memo: formData.memo,
            notify: true
        };

        try {
            const res = await fetch(`${API_URL}/schedule`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });
            if (res.ok) {
                alert("Event Created!");
                closeAddSheet();
                fetchSchedules(); // 리스트 갱신
            } else {
                alert("Failed to create event");
            }
        } catch (err) {
            console.error(err);
            alert("Error creating event");
        }
    };

    // --- 달력 렌더링 ---
    const generateCalendar = () => {
        const monthStart = startOfMonth(currentMonth);
        const monthEnd = endOfMonth(monthStart);
        const startDate = startOfWeek(monthStart);
        const endDate = endOfWeek(monthEnd);

        const dateFormat = "d";
        const rows = [];
        let days = [];
        let day = startDate;
        let formattedDate = "";

        while (day <= endDate) {
            for (let i = 0; i < 7; i++) {
                formattedDate = format(day, dateFormat);
                const cloneDay = day;
                const isSelected = isSameDay(day, selectedDate);
                const isCurrentMonth = isSameMonth(day, monthStart);

                // 해당 날짜에 일정이 있는지 확인 (dot 표시용)
                const dayStr = format(day, 'yyyy-MM-dd');
                const hasEvents = schedules.some(s => s.date === dayStr);

                days.push(
                    <div
                        className={`col cell ${!isCurrentMonth ? "disabled" : ""} ${isSelected ? "selected" : ""}`}
                        key={day}
                        onClick={() => handleDateClick(cloneDay)}
                    >
                        <span className="number">{formattedDate}</span>
                        {/* 일정 있으면 dot 표시 */}
                        {isCurrentMonth && hasEvents && <div className="dot"></div>}
                    </div>
                );
                day = new Date(day.getTime() + 86400000);
            }
            rows.push(
                <div className="row" key={day}>
                    {days}
                </div>
            );
            days = [];
        }
        return <div className="body">{rows}</div>;
    };

    // --- 선택된 날짜의 일정 필터링 ---
    const filteredSchedules = schedules.filter(s => {
        if (!s.date) return false;
        return s.date === format(selectedDate, 'yyyy-MM-dd');
    });

    // --- 드래그 핸들러 (List) ---
    const handleListTouchStart = (e) => {
        dragStartY.current = e.targetTouches[0].clientY;
        dragStartHeight.current = sheetHeight;
    };

    const handleListTouchMove = (e) => {
        const currentY = e.targetTouches[0].clientY;
        const deltaY = currentY - dragStartY.current;
        const deltaVh = (deltaY / window.innerHeight) * 100;
        let newHeight = dragStartHeight.current - deltaVh;

        // 제한 범위
        if (newHeight < 30) newHeight = 30;
        if (newHeight > 85) newHeight = 85;
        setSheetHeight(newHeight);
    };

    // --- 드래그 핸들러 (Add) ---
    const handleAddTouchStart = (e) => {
        addDragStartY.current = e.targetTouches[0].clientY;
        addDragStartHeight.current = addSheetHeight;
    };

    const handleAddTouchMove = (e) => {
        const currentY = e.targetTouches[0].clientY;
        const deltaY = currentY - addDragStartY.current;
        const deltaVh = (deltaY / window.innerHeight) * 100;
        let newHeight = addDragStartHeight.current - deltaVh;

        if (newHeight < 0) newHeight = 0;
        if (newHeight > 90) newHeight = 90;
        setAddSheetHeight(newHeight);
    };

    const handleAddTouchEnd = () => {
        if (addSheetHeight < 40) {
            closeAddSheet();
        } else {
            setAddSheetHeight(85);
        }
    };

    const openAddSheet = () => {
        setIsAddMode(true);
        setAddSheetHeight(85);
        // 초기 폼 데이터 세팅
        setFormData({
            pill_name: "",
            dose: "",
            date: format(selectedDate, 'yyyy-MM-dd'),
            start_time: "",
            end_time: "",
            timing: "",
            memo: "",
        });
    };

    const closeAddSheet = () => {
        setAddSheetHeight(0);
        setTimeout(() => setIsAddMode(false), 300);
    };

    return (
        <div className="calendar-page">
            <div className="calendar-header">
                <div className="icon" onClick={() => setCurrentMonth(subMonths(currentMonth, 1))}>
                    <img src={preIcon} alt="prev" style={{ transform: "rotate(0deg)" }} />
                </div>
                <div className="title">
                    <span className="month">{format(currentMonth, "MMMM")}</span>
                    <span className="year">{format(currentMonth, "yyyy")}</span>
                </div>
                <div className="icon" onClick={() => setCurrentMonth(addMonths(currentMonth, 1))}>
                    <img src={preIcon} alt="next" style={{ transform: "rotate(180deg)" }} />
                </div>
            </div>

            <div className="calendar-weekdays">
                <div>Mon</div><div>Tue</div><div>Wed</div><div>Thu</div><div>Fri</div><div>Sat</div><div>Sun</div>
            </div>

            {generateCalendar()}

            {/* --- 스케줄 리스트 시트 --- */}
            <div
                className="schedule-sheet"
                style={{ height: `${sheetHeight}vh`, transition: 'height 0.1s linear' }}
                ref={listSheetRef}
            >
                <div
                    className="sheet-handle-bar"
                    onTouchStart={handleListTouchStart}
                    onTouchMove={handleListTouchMove}
                >
                    <div className="handle"></div>
                </div>

                <div className="sheet-content">
                    {filteredSchedules.length === 0 ? (
                        <div style={{ textAlign: 'center', color: '#ccc', marginTop: '20px' }}>
                            No pills for today.
                        </div>
                    ) : (
                        filteredSchedules.map((item) => (
                            <div className="event-card" key={item.id}>
                                <div className="event-time">
                                    <span className="dot" style={{ borderColor: '#9F63FF' }}></span>
                                    {item.timing || "Anytime"}
                                </div>
                                <div className="event-title">{item.pill_name}</div>
                                <div className="event-desc">{item.memo || item.dose}</div>
                            </div>
                        ))
                    )}
                </div>

                {!isAddMode && (
                    <div className="fab-add" onClick={openAddSheet}>+</div>
                )}
            </div>

            {/* --- 복용약 추가 시트 --- */}
            <div
                className={`add-pill-sheet`}
                style={{ height: `${addSheetHeight}vh`, bottom: isAddMode ? 0 : '-100vh' }}
                ref={addSheetRef}
            >
                <div
                    className="sheet-handle-bar"
                    onTouchStart={handleAddTouchStart}
                    onTouchMove={handleAddTouchMove}
                    onTouchEnd={handleAddTouchEnd}
                >
                    <div className="handle"></div>
                </div>

                <div className="sheet-header">
                    <h3>Add New Pill</h3>
                </div>

                <div className="sheet-content-scroll">
                    <div className="form-group">
                        <label>Pill name*</label>
                        <input name="pill_name" value={formData.pill_name} onChange={handleFormChange} placeholder="Pill name" />
                    </div>
                    <div className="form-group">
                        <label>dose</label>
                        <input name="dose" value={formData.dose} onChange={handleFormChange} placeholder="dose" />
                    </div>
                    <div className="form-group">
                        <label>Date</label>
                        <div className="input-with-icon">
                            <input name="date" value={formData.date} onChange={handleFormChange} placeholder="YYYY-MM-DD" />
                        </div>
                    </div>
                    <div className="row-group">
                        <div className="form-group half">
                            <label>Start time</label>
                            <input name="start_time" value={formData.start_time} onChange={handleFormChange} placeholder="10:00" />
                        </div>
                        <div className="form-group half">
                            <label>End time</label>
                            <input name="end_time" value={formData.end_time} onChange={handleFormChange} placeholder="12:00" />
                        </div>
                    </div>
                    <div className="form-group">
                        <label>timing</label>
                        <input name="timing" value={formData.timing} onChange={handleFormChange} placeholder="timing (e.g. After meal)" />
                    </div>
                    <div className="form-group">
                        <label>memo</label>
                        <textarea name="memo" value={formData.memo} onChange={handleFormChange} placeholder="memo" rows={3}></textarea>
                    </div>

                    <div className="form-group">
                        <label>Select User</label>
                        <div className="user-select">
                            <div className="user-chip selected"><span className="dot"></span> User1</div>
                        </div>
                    </div>

                    <button className="create-btn" onClick={handleSubmit}>
                        Create Event
                    </button>
                    <div style={{ height: '100px' }}></div>
                </div>
            </div>

            <div className="bottom-nav-container">
                <HomeBar />
            </div>
        </div>
    );
};

export default Calendar;
