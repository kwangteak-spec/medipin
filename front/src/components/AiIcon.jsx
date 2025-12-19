// src/components/AiIcon.jsx
import React from "react";

export const AiIcon = ({ className }) => {
  return (
    <div
      className={className}
      style={{
        width: 48,
        height: 48,
        borderRadius: "50%",
        backgroundColor: "#9f63ff",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        color: "#fff",
        fontWeight: "bold",
        fontSize: 14,
      }}
    >
      AI
    </div>
  );
};
