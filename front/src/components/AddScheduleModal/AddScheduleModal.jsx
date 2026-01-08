import React, { useState, useEffect } from "react";
import { format } from "date-fns";
import { API_BASE_URL } from "../../api/config";
import { Warning } from "../Warning/Warning";
import { CalendarIcon } from "../Icons";
import "./style.css";

const AddScheduleModal = ({ isOpen, onClose, defaultPillName }) => {
    const [formData, setFormData] = useState({
        pill_name: "",
        dose: "",
        start_date: format(new Date(), 'yyyy-MM-dd'),
        end_date: format(new Date(), 'yyyy-MM-dd'),
        timing: "",
        memo: "",
    });

    const [users, setUsers] = useState([]);
    const [selectedUserId, setSelectedUserId] = useState(null);
    const [loading, setLoading] = useState(false);
    const [warningType, setWarningType] = useState(null);

    // ⏰ 다중 복약 시간 상태
    const [timings, setTimings] = useState([{ hour: '', minute: '', text: '' }]);

    useEffect(() => {
        if (isOpen) {
            setFormData(prev => ({
                ...prev,
                pill_name: defaultPillName || "",
                start_date: format(new Date(), 'yyyy-MM-dd'),
                end_date: format(new Date(), 'yyyy-MM-dd'),
            }));
            setTimings([{ hour: '', minute: '', text: '' }]);
            fetchUsers();
        }
    }, [isOpen, defaultPillName]);

    const fetchUsers = async () => {
        const token = localStorage.getItem("authToken");
        if (!token) return;

        try {
            // Fetch main profile and family members
            const [profileRes, familyRes] = await Promise.all([
                fetch(`${API_BASE_URL}/user/profile`, {
                    headers: { Authorization: `Bearer ${token}` }
                }),
                fetch(`${API_BASE_URL}/user/family`, {
                    headers: { Authorization: `Bearer ${token}` }
                })
            ]);

            let allUsers = [];
            if (profileRes.ok) {
                const mainUser = await profileRes.json();
                allUsers.push({ id: mainUser.id, name: mainUser.name + " (Me)" });
                setSelectedUserId(mainUser.id);
            }
            if (familyRes.ok) {
                const family = await familyRes.json();
                allUsers = [...allUsers, ...family.map(f => ({ id: f.id, name: f.name }))];
            }
            setUsers(allUsers);
        } catch (err) {
            console.error("Failed to fetch users:", err);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleWarningClose = () => {
        setWarningType(null);
        if (warningType === "medication-complete") {
            onClose();
        }
    };

    const handleSubmit = async () => {
        if (!formData.pill_name) {
            alert("약 이름은 필수입니다.");
            return;
        }

        if (!selectedUserId) {
            alert("사용자 정보가 로드되지 않았습니다. 잠시 후 다시 시도하거나 다시 로그인해주세요.");
            return;
        }

        setLoading(true);
        // ⏰ timings 배열 구성
        const validTimings = timings
            .filter(t => t.hour && t.minute)
            .map(t => `${t.hour}:${t.minute}`);

        const payload = {
            user_id: selectedUserId,
            pill_name: formData.pill_name,
            dose: formData.dose,
            start_date: formData.start_date,
            end_date: formData.end_date,
            timing: validTimings.length > 0 ? validTimings[0] : formData.timing,
            timings: validTimings,
            meal_relation: null,
            memo: formData.memo,
            notify: true,
            is_taken: false,
        };

        try {
            const res = await fetch(`${API_BASE_URL}/medication/schedule`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                setWarningType("medication-complete");
            } else {
                const err = await res.json();
                alert(`등록 실패: ${err.detail || "오류가 발생했습니다."}`);
            }
        } catch (error) {
            console.error(error);
            alert("서버 통신 오류");
        } finally {
            setLoading(false);
        }
    };

    if (!isOpen) return null;

    return (
        <>
            {warningType && <Warning one={warningType} onClose={handleWarningClose} />}

            <div className="add-schedule-modal-overlay">
                <div className="add-schedule-modal">
                    <div className="modal-header">
                        <h3>Add new Pill</h3>
                        <button className="close-btn" onClick={onClose}>×</button>
                    </div>
                    <div className="modal-content">
                        <div className="form-group">
                            <label>Pill name*</label>
                            <input name="pill_name" value={formData.pill_name} onChange={handleChange} placeholder="Pill name" />
                        </div>
                        <div className="form-group">
                            <label>dose</label>
                            <input name="dose" value={formData.dose} onChange={handleChange} placeholder="dose" />
                        </div>

                        <div className="row-group">
                            <div className="form-group half">
                                <label>start date*</label>
                                <input type="date" name="start_date" value={formData.start_date} onChange={handleChange} required />
                                <div className="input-icon">
                                    <CalendarIcon />
                                </div>
                            </div>
                            <div className="form-group half">
                                <label>end date*</label>
                                <input type="date" name="end_date" value={formData.end_date} onChange={handleChange} required />
                                <div className="input-icon">
                                    <CalendarIcon />
                                </div>
                            </div>
                        </div>

                        <div className="form-group">
                            <label>Timing (Max 5)</label>
                            <div className="timing-list">
                                {timings.map((t, idx) => (
                                    <div key={idx} className="timing-row" style={{ display: 'flex', gap: '5px', marginBottom: '5px' }}>
                                        <select
                                            className="timing-select"
                                            value={t.hour}
                                            onChange={(e) => {
                                                const newTimings = [...timings];
                                                newTimings[idx].hour = e.target.value;
                                                if (idx === timings.length - 1 && timings.length < 5 && e.target.value && newTimings[idx].minute) {
                                                    newTimings.push({ hour: '', minute: '', text: '' });
                                                }
                                                setTimings(newTimings);
                                            }}
                                            style={{ flex: 1, padding: '8px', borderRadius: '8px', border: '1px solid #ddd', backgroundColor: '#F0EBFF' }}
                                        >
                                            <option value="">Hour</option>
                                            {[...Array(24)].map((_, i) => {
                                                const val = i.toString().padStart(2, '0');
                                                return <option key={val} value={val}>{val}</option>;
                                            })}
                                        </select>
                                        <span style={{ alignSelf: 'center' }}>:</span>
                                        <select
                                            className="timing-select"
                                            value={t.minute}
                                            onChange={(e) => {
                                                const newTimings = [...timings];
                                                newTimings[idx].minute = e.target.value;
                                                if (idx === timings.length - 1 && timings.length < 5 && e.target.value && newTimings[idx].hour) {
                                                    newTimings.push({ hour: '', minute: '', text: '' });
                                                }
                                                setTimings(newTimings);
                                            }}
                                            style={{ flex: 1, padding: '8px', borderRadius: '8px', border: '1px solid #ddd', backgroundColor: '#F0EBFF' }}
                                        >
                                            <option value="">Min</option>
                                            {[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55].map((i) => {
                                                const val = i.toString().padStart(2, '0');
                                                return <option key={val} value={val}>{val}</option>;
                                            })}
                                        </select>
                                        {timings.length > 1 && (
                                            <button
                                                onClick={() => {
                                                    const newTimings = timings.filter((_, i) => i !== idx);
                                                    setTimings(newTimings);
                                                }}
                                                style={{ background: 'none', border: 'none', color: '#ff4444', cursor: 'pointer', marginLeft: '5px' }}
                                            >
                                                ✕
                                            </button>
                                        )}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="form-group">
                            <label>memo</label>
                            <textarea name="memo" value={formData.memo} onChange={handleChange} rows={2} placeholder="memo"></textarea>
                        </div>

                        <div className="form-group">
                            <label>Select User</label>
                            <div className="user-select">
                                {users.map((u, index) => {
                                    const dotColorClass = ["purple", "green", "blue"][index % 3];
                                    return (
                                        <div
                                            key={u.id}
                                            className={`user-chip ${selectedUserId === u.id ? 'selected' : ''}`}
                                            onClick={() => setSelectedUserId(u.id)}
                                        >
                                            <span className={`dot ${dotColorClass}`}></span> {u.name}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        <button className="submit-btn" onClick={handleSubmit} disabled={loading}>
                            {loading ? "Registering..." : "Register Pill"}
                        </button>
                    </div>
                </div>
            </div>
        </>
    );
};

export default AddScheduleModal;
