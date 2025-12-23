import PropTypes from "prop-types";
import React from "react";
import "./style.css";

export const Button = ({ one = "login", className = "", onClick, disabled }) => {
  return (
    <button
      type="button"
      className={`button button--${one} ${className}`}
      onClick={onClick}
      disabled={disabled}
    >
      {one === "login" && "login"}
      {one === "register" && "Register"}
      {one === "three" && "Edit"}
      {one === "four" && "+"}
      {one === "five" && "Create Event"}
    </button>
  );
};

Button.propTypes = {
  one: PropTypes.oneOf(["login", "register", "three", "four", "five"]),
  className: PropTypes.string,
  onClick: PropTypes.func,
};
