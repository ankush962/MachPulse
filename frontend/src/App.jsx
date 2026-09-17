import {
  useEffect,
  useRef,
  useState,
} from "react";

import {
  connectMonitor,
} from "./services/websocket";

import "./App.css";


function App() {

  const socketRef = useRef(null);

  const [connected, setConnected] =
    useState(false);

  const [demoMode, setDemoMode] =
    useState(true);

  const [machineId, setMachineId] =
    useState("M01");

  const [data, setData] =
    useState(null);

  const [history, setHistory] =
    useState([]);

  const connect = () => {

    socketRef.current?.close();

    const socket =
      connectMonitor({
        machineId,
        demo: demoMode,

        onOpen: () => {
          setConnected(true);
        },

        onClose: () => {
          setConnected(false);
        },

        onError: (error) => {
          console.error(error);
          setConnected(false);
        },

        onMessage: (message) => {

          if (
            message.status !== "ok"
          ) {
            return;
          }

          setData(message);

          const health =
            message.analysis?.health_score;

          if (
            typeof health === "number"
          ) {
            setHistory((previous) => [
              ...previous.slice(-19),
              health,
            ]);
          }
        },
      });

    socketRef.current = socket;
  };


  const disconnect = () => {

    socketRef.current?.close();

    socketRef.current = null;

    setConnected(false);
  };


  useEffect(() => {

    return () => {
      socketRef.current?.close();
    };

  }, []);


  const analysis =
    data?.analysis || {};

  const features =
    data?.features || {};


  const health =
    Number(
      analysis.health_score ?? 100
    );

  const risk =
    analysis.risk ?? "LOW";


  return (
    <div className="app">

      <header className="header">

        <div>
          <div className="brand">
            MachPulse
          </div>

          <div className="subtitle">
            Predict machine problems
            before downtime.
          </div>
        </div>

        <div
          className={
            connected
              ? "status connected"
              : "status"
          }
        >
          <span />
          {connected
            ? "Connected"
            : "Disconnected"}
        </div>

      </header>


      <main className="content">

        <section className="controls">

          <input
            value={machineId}
            onChange={(event) =>
              setMachineId(
                event.target.value
              )
            }
            placeholder="Machine ID"
          />

          <label>
            <input
              type="checkbox"
              checked={demoMode}
              onChange={(event) =>
                setDemoMode(
                  event.target.checked
                )
              }
            />
            Demo Mode
          </label>

          <button
            onClick={connect}
          >
            Start Monitoring
          </button>

          <button
            className="secondary"
            onClick={disconnect}
          >
            Stop
          </button>

        </section>


        <section className="grid">

          <div className="card health-card">

            <div className="card-title">
              Machine Health
            </div>

            <div
              className={
                `health-value ${
                  health < 60
                    ? "danger"
                    : health < 80
                    ? "warning"
                    : ""
                }`
              }
            >
              {health.toFixed(0)}
              <span>/100</span>
            </div>

            <div className="risk">
              Risk: {risk}
            </div>

          </div>


          <div className="card">

            <div className="card-title">
              Vibration
            </div>

            <div className="metric">
              RMS
              <strong>
                {Number(
                  features.rms ?? 0
                ).toFixed(3)}
              </strong>
            </div>

            <div className="metric">
              Dominant Frequency
              <strong>
                {Number(
                  features.dominant_frequency ?? 0
                ).toFixed(2)}
                Hz
              </strong>
            </div>

          </div>


          <div className="card">

            <div className="card-title">
              Detection
            </div>

            <div
              className={
                analysis.is_anomaly
                  ? "alert active"
                  : "alert"
              }
            >
              {analysis.is_anomaly
                ? "ANOMALY DETECTED"
                : "Machine operating normally"}
            </div>

            <div className="metric">
              Anomaly Score
              <strong>
                {Number(
                  analysis.anomaly_score ?? 0
                ).toFixed(2)}
              </strong>
            </div>

          </div>

        </section>


        <section className="card">

          <div className="card-title">
            Health Trend
          </div>

          <div className="bars">

            {history.map(
              (value, index) => (
                <div
                  className="bar-wrapper"
                  key={index}
                >
                  <div
                    className="bar"
                    style={{
                      height:
                        `${Math.max(
                          value,
                          5
                        )}%`,
                    }}
                  />
                </div>
              )
            )}

          </div>

        </section>


        <section className="card">

          <div className="card-title">
            Maintenance Advisor
          </div>

          {data?.ai_advice ? (

            <div className="advice">
              {data.ai_advice}
            </div>

          ) : analysis.status ===
            "calibrating" ? (

            <div className="advice">
              Calibrating machine baseline...
              <br />
              Window{" "}
              {analysis.calibration_progress}
              {" / "}
              {analysis.calibration_total}
            </div>

          ) : (

            <div className="advice muted">
              No maintenance action
              required right now.
            </div>

          )}

        </section>

      </main>

    </div>
  );
}


export default App;