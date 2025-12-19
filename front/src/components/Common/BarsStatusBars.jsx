/*
We're constantly improving the code you see. 
Please share your feedback here: https://form.asana.com/?k=uvp-HPgd3_hyoXRBw1IcNg&d=1152665201300829
*/

import React from "react";
import "./style.css";

export const BarsStatusBars = ({
  className,
  timeClassName,
  battery = "https://c.animaapp.com/Ch8tSI1y/img/battery@2x.png",
  wifi = "https://c.animaapp.com/Ch8tSI1y/img/wifi.svg",
  cellularConnection = "https://c.animaapp.com/Ch8tSI1y/img/cellular-connection.svg",
}) => {
  return (
    <div className={`bars-status-bars ${className}`}>
      <div className="time-style">
        <div className={`time ${timeClassName}`}>9:41</div>
      </div>

      <img className="battery" alt="Battery" src={battery} />

      <img className="wifi" alt="Wifi" src={wifi} />

      <img
        className="cellular-connection"
        alt="Cellular connection"
        src={cellularConnection}
      />
    </div>
  );
};
