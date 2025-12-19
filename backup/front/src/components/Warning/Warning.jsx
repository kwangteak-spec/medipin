import PropTypes from "prop-types";
import React from "react";
import line from "./warning_line.svg";   // 공통 라인 파일 1개
import "./style.css";

export const Warning = ({ one, className }) => {
  return (
    <div className={`warning-overlay ${one} ${className}`}>
      {(one === "eight" ||
        one === "forget-password" ||
        one === "incorrect-password-confirm" ||
        one === "incorrect-password" ||
        one === "register-complete" ||
        one === "unrequire-email" ||
        one === "unrequire-password") && (
        <div className="warning-popup">
          <div className="frame">
            <div className="div">
              <div className="service-is-not-ready">
                {one === "forget-password" && <>Service is not ready!</>}
                {one === "incorrect-password" && <>Incorrect password!</>}
                {one === "unrequire-password" && <>Password doesn’t meet the requirements!</>}
                {one === "incorrect-password-confirm" && <>Password do not match!</>}
                {one === "unrequire-email" && <>Invalid email format!</>}
                {["eight", "register-complete"].includes(one) && <>Registration complete!</>}
              </div>

              {/* 라인 파일 하나만 */}
              <img className="line" alt="Line" src={line} />
            </div>

            <div className="service-is-currently">
              {one === "forget-password" && (
                <p>
                  Service is currently under developmet.
                  <br />
                  Please try again later! :-)
                </p>
              )}

              {["incorrect-password", "unrequire-password"].includes(one) && (
                <p>
                  The password you entered is incorrect.
                  <br />
                  Please check and try again.
                </p>
              )}

              {one === "incorrect-password-confirm" && (
                <p>
                  Please make sure your password
                  <br />
                  and confirmation password
                  <br />
                  are the same.
                </p>
              )}

              {one === "unrequire-email" && (
                <p>
                  Please enter a valid email address.
                  <br />
                  Check the format and try again.
                </p>
              )}

              {["eight", "register-complete"].includes(one) && (
                <p>
                  Enjoy our service <br />
                  and have a great time using it!
                </p>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

Warning.propTypes = {
  one: PropTypes.oneOf([
    "unrequire-email",
    "forget-password",
    "incorrect-password",
    "unrequire-password",
    "register-complete",
    "hidden",
    "eight",
    "incorrect-password-confirm",
  ]),
};
