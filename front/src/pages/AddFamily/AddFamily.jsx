import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./style.css"; // Modern form style
import { API_BASE_URL } from "../../api/config";
import { BackIcon, CalendarIcon } from "../../components/Icons";

const AddFamily = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        name: "",
        birthdate: "",
        gender: "male",
        height: "",
        weight: "",
        special_note: ""
    });

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleGenderSelect = (gender) => {
        setFormData({ ...formData, gender });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem("authToken");

        const birthDate = new Date(formData.birthdate);
        const today = new Date();
        let age = today.getFullYear() - birthDate.getFullYear();
        const m = today.getMonth() - birthDate.getMonth();
        if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
            age--;
        }
        if (isNaN(age)) age = 0;

        const payload = {
            name: formData.name,
            age: age,
            birth_date: formData.birthdate,
            gender: formData.gender,
            height: formData.height ? parseFloat(formData.height) : null,
            weight: formData.weight ? parseFloat(formData.weight) : null,
            special_note: formData.special_note
        };

        try {
            const res = await fetch(`${API_BASE_URL}/user/family`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: `Bearer ${token}`
                },
                body: JSON.stringify(payload)
            });

            if (res.ok) {
                alert("가족 구성원이 추가되었습니다.");
                navigate("/mypage");
            } else {
                const err = await res.json();
                alert("오류 발생: " + JSON.stringify(err));
            }
        } catch (error) {
            console.error("Add family error:", error);
            alert("서버 오류가 발생했습니다.");
        }
    };

    // Icons removed - now using centralized Icons component

    return (
        <div className="add-family-page">
            {/* Header matching EditProfile style */}
            <div className="add-family-header">
                <button onClick={() => navigate(-1)} className="back-btn">
                    <BackIcon />
                </button>
                <div className="header-title">Add Family</div>
            </div>

            <div className="add-family-content">
                <form onSubmit={handleSubmit}>
                    {/* Name */}
                    <div className="form-group">
                        <label>Name</label>
                        <input
                            type="text"
                            name="name"
                            placeholder="Enter family member's name"
                            value={formData.name}
                            onChange={handleChange}
                            required
                        />
                    </div>

                    {/* Birthdate & Gender */}
                    <div className="row-group">
                        <div className="form-group half">
                            <label>Birthdate</label>
                            <input
                                type="date"
                                name="birthdate"
                                value={formData.birthdate}
                                onChange={handleChange}
                                required
                            />
                        </div>

                        <div className="form-group" style={{ width: '120px' }}>
                            <label>Gender</label>
                            <select
                                name="gender"
                                value={formData.gender}
                                onChange={handleChange}
                            >
                                <option value="male">Male</option>
                                <option value="female">Female</option>
                            </select>
                        </div>
                    </div>

                    {/* Height & Weight */}
                    <div className="row-group">
                        <div className="form-group half">
                            <label>Height (cm)</label>
                            <input
                                type="number"
                                name="height"
                                placeholder="cm"
                                value={formData.height}
                                onChange={handleChange}
                            />
                        </div>

                        <div className="form-group half">
                            <label>Weight (kg)</label>
                            <input
                                type="number"
                                name="weight"
                                placeholder="kg"
                                value={formData.weight}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    {/* Special Note */}
                    <div className="form-group">
                        <label>Special Note (Allergies, etc)</label>
                        <textarea
                            name="special_note"
                            placeholder="Memo"
                            value={formData.special_note}
                            onChange={handleChange}
                            rows={3}
                        />
                    </div>

                    <button type="submit" className="add-family-submit-btn">
                        Create Family Member
                    </button>
                    <div style={{ height: '100px' }}></div>
                </form>
            </div>
        </div>
    );
};

export default AddFamily;
