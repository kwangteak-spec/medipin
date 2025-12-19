import React from "react";
import addIcon from "./add_icon.svg";
import "./style.css";

export const SearchResultIn = ({
  className,
  imageUrl,
  title,
  onPlusClick,
  onImageClick,
}) => {
  return (
    <div className={`search-result-in ${className}`}>
      <div className="search-result">
        <div className="frame">
          <div className="image-icon" onClick={onImageClick} style={{ cursor: "pointer" }}>
            {imageUrl ? (
              <img
                src={imageUrl}
                alt={title}
                className="drug-db-image"
              />
            ) : (
              <div className="image-placeholder">NO IMAGE</div>
            )}
          </div>

          <div className="text-wrapper">{title}</div>
        </div>
      </div>

      <img
        className="frame-2"
        alt="add"
        src={addIcon}
        onClick={onPlusClick}
      />
    </div>
  );
};
