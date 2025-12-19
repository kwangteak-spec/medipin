// src/components/ChatbubbleEllipsesOutline.jsx
import React from "react";

export const ChatbubbleEllipsesOutline = ({ className }) => {
  return (
    <div
      className={className}
      style={{
        width: 26,
        height: 26,
        borderRadius: "50%",
        backgroundColor: "#fff",
        color: "#9f63ff",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontSize: 12,
        fontWeight: "bold",
      }}
    >
      💬
    </div>
  );
};
