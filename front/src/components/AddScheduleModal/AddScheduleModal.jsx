import React, { useState, useEffect } from "react";
import { format } from "date-fns";
import { API_BASE_URL } from "../../api/config";
import { Warning } from "../Warning/Warning";
import { Button } from "../Button/Button";
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

    const [loading, setLoading] = useState(false);
    const [warningType, setWarningType] = useState(null); // Warning state

    useEffect(() => {
        console.log("AddScheduleModal useEffect - isOpen:", isOpen, "defaultPillName:", defaultPillName);
        if (isOpen) {
            setFormData(prev => ({
                ...prev,
                pill_name: defaultPillName || ""
            }));
        }
    }, [isOpen, defaultPillName]);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

    const handleWarningClose = () => {
        setWarningType(null);
        if (warningType === "medication-complete") {
            onClose(); // Close modal on success warning close
        }
    };

    const handleSubmit = async () => {
        if (!formData.pill_name) {
            alert("약 이름은 필수입니다.");
            return;
        }

        setLoading(true);
        const storedUserId = localStorage.getItem("userId");
        const USER_ID = storedUserId ? parseInt(storedUserId) : 1;

        const payload = {
            user_id: USER_ID,
            pill_name: formData.pill_name,
            dose: formData.dose,
            start_date: formData.start_date,
            end_date: formData.end_date,
            timing: formData.timing,
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
                // Show custom warning instead of alert
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
                        <h3>Add Medication Schedule</h3>
                        <button className="close-btn" onClick={onClose}>×</button>
                    </div>
                    <div className="modal-content">
                        <div className="form-group">
                            <label>pill name</label>
                            <input name="pill_name" value={formData.pill_name} onChange={handleChange} placeholder="약 이름" />
                        </div>
                        <div className="form-group">
                            <label>Dose (1정 등)</label>
                            <input name="dose" value={formData.dose} onChange={handleChange} placeholder="예: 1정" />
                        </div>

                        <div className="row-group">
                            <div className="form-group half">
                                <label>start date</label>
                                <input type="date" name="start_date" value={formData.start_date} onChange={handleChange} />
                            </div>
                            <div className="form-group half">
                                <label>end date</label>
                                <input type="date" name="end_date" value={formData.end_date} onChange={handleChange} />
                            </div>
                        </div>

                        <div className="form-group">
                            <label>timing (식후 30분 등)</label>
                            <input name="timing" value={formData.timing} onChange={handleChange} placeholder="예: 식후 30분" />
                        </div>
                        <div className="form-group">
                            <label>memo</label>
                            <textarea name="memo" value={formData.memo} onChange={handleChange} rows={3} placeholder="메모 입력"></textarea>
                        </div>

                        <Button one="register" onClick={handleSubmit} disabled={loading} />
                    </div>
                </div>
            </div>
        </>
    );
};

export default AddScheduleModal;
