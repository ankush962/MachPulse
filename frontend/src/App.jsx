import {
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";

import {
  connectMonitor,
} from "./services/websocket";

import "./App.css";


const MAX_HISTORY = 30;


function formatNumber(
  value,
  digits = 2
) {
  const number = Number(value);

  if (!Number.isFinite(number)) {
    return "--";
  }

  return number.toFixed(digits);
}


function riskClass(risk) {
  switch (String(risk).toUpperCase()) {
    case "CRITICAL":
      return "critical";

    case "HIGH":
      return "high";

    case "MEDIUM":
      return "medium";

    default:
      return "low";
  }
}


function HealthGauge({
  health,
  risk,
}) {
  const radius = 88;
  const circumference =
    2 * Math.PI * radius;

  const progress =
    circumference *
    Math.min(
      Math.max(health, 0),
      100
    ) /
    100;

  return (
    <div className="health-gauge">

      <svg
        className="health-ring"
        viewBox="0 0 220 220"
      >
        <circle
          className="health-ring-track"
          cx="110"
          cy="110"
          r={radius}
        />

        <circle
          className={`health-ring-value ${riskClass(
            risk
          )}`}
          cx="110"
          cy="110"
          r={radius}
          strokeDasharray={circumference}
          strokeDashoffset={
            circumference - progress
          }
        />
      </svg>

      <div className="health-gauge-content">

        <div className="health-number">
          {Math.round(health)}
        </div>

        <div className="health-total">
          /100
        </div>

        <div
          className={`health-status ${riskClass(
            risk
          )}`}
        >
          {risk === "CRITICAL"
            ? "CRITICAL"
            : risk === "HIGH"
            ? "HIGH RISK"
            : risk === "MEDIUM"
            ? "MEDIUM RISK"
            : "HEALTHY"}
        </div>

      </div>
    </div>
  );
}


function MetricCard({
  label,
  value,
  unit,
  description,
}) {
  return (
    <div className="metric-card">

      <div className="metric-label">
        {label}
      </div>

      <div className="metric-main">
        <span>
          {value}
        </span>

        {unit && (
          <small>{unit}</small>
        )}
      </div>

      {description && (
        <div className="metric-description">
          {description}
        </div>
      )}

    </div>
  );
}


function HealthTrend({
  history,
}) {
  const width = 760;
  const height = 180;
  const padding = 12;

  const points = useMemo(() => {

    if (history.length === 0) {
      return "";
    }

    const usableWidth =
      width - padding * 2;

    const usableHeight =
      height - padding * 2;

    return history
      .map((value, index) => {

        const x =
          padding +
          (index /
            Math.max(
              history.length - 1,
              1
            )) *
            usableWidth;

        const y =
          padding +
          ((100 - value) / 100) *
            usableHeight;

        return `${x},${y}`;

      })
      .join(" ");
  }, [history]);


  return (
    <div className="trend-container">

      {history.length > 1 ? (
        <svg
          className="trend-svg"
          viewBox={`0 0 ${width} ${height}`}
          preserveAspectRatio="none"
        >

          <defs>
            <linearGradient
              id="trendFill"
              x1="0"
              y1="0"
              x2="0"
              y2="1"
            >
              <stop
                offset="0%"
                stopColor="rgba(74, 222, 128, 0.20)"
              />

              <stop
                offset="100%"
                stopColor="rgba(74, 222, 128, 0)"
              />
            </linearGradient>
          </defs>

          <line
            className="trend-grid-line"
            x1="0"
            y1="45"
            x2={width}
            y2="45"
          />

          <line
            className="trend-grid-line"
            x1="0"
            y1="90"
            x2={width}
            y2="90"
          />

          <line
            className="trend-grid-line"
            x1="0"
            y1="135"
            x2={width}
            y2="135"
          />

          <polyline
            points={points}
            className="trend-line"
            fill="none"
          />

        </svg>
      ) : (
        <div className="empty-trend">
          Waiting for monitoring data...
        </div>
      )}

      <div className="trend-scale">
        <span>100</span>
        <span>75</span>
        <span>50</span>
        <span>25</span>
        <span>0</span>
      </div>

    </div>
  );
}


function App() {

  const socketRef =
    useRef(null);


  const [machineId, setMachineId] =
    useState("M01");

  const [demoMode, setDemoMode] =
    useState(false);

  const [connected, setConnected] =
    useState(false);

  const [data, setData] =
    useState(null);

  const [history, setHistory] =
    useState([]);

  const [connectionError, setConnectionError] =
    useState("");


  const connect = () => {

    socketRef.current?.close();

    setConnectionError("");
    setData(null);
    setHistory([]);

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

        onError: () => {
          setConnected(false);

          setConnectionError(
            "Unable to connect to MachPulse backend."
          );
        },

        onMessage: (message) => {

          if (
            message.status ===
            "connected"
          ) {
            return;
          }

          if (
            message.status !==
            "ok"
          ) {
            console.warn(
              "Backend:",
              message
            );

            return;
          }

          setData(message);


          const health =
            Number(
              message.analysis
                ?.health_score
            );


          if (
            Number.isFinite(health)
          ) {

            setHistory(
              previous => [
                ...previous.slice(
                  -(MAX_HISTORY - 1)
                ),
                health,
              ]
            );
          }
        },
      });

    socketRef.current =
      socket;
  };


  const disconnect = () => {

    socketRef.current?.close();

    socketRef.current =
      null;

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


  const health = Number(
    analysis.health_score ??
      100
  );


  const risk =
    analysis.risk ??
    "LOW";


  const anomaly =
    Boolean(
      analysis.is_anomaly
    );


  const calibrated =
    Boolean(
      analysis.calibrated
    );


  const calibrationProgress =
    Number(
      analysis.calibration_progress ??
        0
    );


  const calibrationTotal =
    Number(
      analysis.calibration_total ??
        10
    );


  const calibrationPercent =
    calibrationTotal > 0
      ? Math.min(
          100,
          (
            calibrationProgress /
            calibrationTotal
          ) *
            100
        )
      : 0;


  const lastUpdate =
    data?.timestamp
      ? new Date(
          Number(data.timestamp) *
            1000
        ).toLocaleTimeString()
      : "--";


  const statusLabel =
    anomaly
      ? "Anomaly detected"
      : calibrated
      ? "Monitoring normally"
      : "Calibrating baseline";


  return (
    <div className="app-shell">

      {/* HEADER */}

      <header className="topbar">

        <div className="brand-block">

          <div className="brand-mark">
            MP
          </div>

          <div>
            <div className="brand-name">
              MachPulse
            </div>

            <div className="brand-subtitle">
              Machine Health Intelligence
            </div>
          </div>

        </div>


        <div className="topbar-right">

          <div className="connection-chip">

            <span
              className={`connection-dot ${
                connected
                  ? "online"
                  : ""
              }`}
            />

            {connected
              ? "LIVE"
              : "OFFLINE"}

          </div>

          <div className="machine-chip">

            <span>
              MACHINE
            </span>

            <strong>
              {machineId}
            </strong>

          </div>

        </div>

      </header>


      <main className="dashboard">

        {/* MACHINE HEADER */}

        <section className="machine-header">

          <div>

            <div className="eyebrow">
              REAL-TIME MACHINE MONITORING
            </div>

            <h1>
              {machineId}
              <span>
                Machine Health
              </span>
            </h1>

            <p>
              Smartphone vibration intelligence
              for early anomaly detection.
            </p>

          </div>


          <div className="machine-meta">

            <div>
              <span>
                DATA SOURCE
              </span>

              <strong>
                {demoMode
                  ? "Synthetic Demo"
                  : "Android Accelerometer"}
              </strong>
            </div>

            <div>
              <span>
                LAST UPDATE
              </span>

              <strong>
                {lastUpdate}
              </strong>
            </div>

          </div>

        </section>


        {connectionError && (
          <div className="error-banner">
            <strong>
              Connection issue
            </strong>

            <span>
              {connectionError}
            </span>
          </div>
        )}


        {/* CONTROL BAR */}

        <section className="control-bar">

          <div className="control-group">

            <label>
              Machine ID
            </label>

            <input
              value={machineId}
              onChange={event =>
                setMachineId(
                  event.target.value
                )
              }
              disabled={connected}
            />

          </div>


          <label className="toggle-control">

            <input
              type="checkbox"
              checked={demoMode}
              onChange={event =>
                setDemoMode(
                  event.target.checked
                )
              }
              disabled={connected}
            />

            <span className="toggle-slider" />

            <span>
              Demo Mode
            </span>

          </label>


          <div className="control-actions">

            {!connected ? (

              <button
                className="primary-button"
                onClick={connect}
              >
                Start Monitoring
              </button>

            ) : (

              <button
                className="danger-button"
                onClick={disconnect}
              >
                Stop Monitoring
              </button>

            )}

          </div>

        </section>


        {/* TOP GRID */}

        <section className="hero-grid">

          {/* HEALTH */}

          <div className="panel health-panel">

            <div className="panel-header">

              <div>
                <div className="panel-kicker">
                  MACHINE HEALTH
                </div>

                <h2>
                  Overall Condition
                </h2>
              </div>

              <div
                className={`state-pill ${riskClass(
                  risk
                )}`}
              >
                <span />
                {risk}
              </div>

            </div>


            <div className="health-layout">

              <HealthGauge
                health={
                  Number.isFinite(
                    health
                  )
                    ? health
                    : 100
                }
                risk={risk}
              />


              <div className="health-summary">

                <div className="summary-row">

                  <span>
                    System state
                  </span>

                  <strong>
                    {statusLabel}
                  </strong>

                </div>


                <div className="summary-row">

                  <span>
                    Anomaly score
                  </span>

                  <strong>
                    {formatNumber(
                      analysis.anomaly_score,
                      2
                    )}
                  </strong>

                </div>


                <div className="summary-row">

                  <span>
                    Baseline
                  </span>

                  <strong>
                    {calibrated
                      ? "Ready"
                      : "Learning"}
                  </strong>

                </div>


                {anomaly && (
                  <div className="alert-box">

                    <div className="alert-icon">
                      !
                    </div>

                    <div>

                      <strong>
                        Anomaly detected
                      </strong>

                      <p>
                        Current vibration
                        behavior deviates
                        from the learned
                        baseline.
                      </p>

                    </div>

                  </div>
                )}

              </div>

            </div>

          </div>


          {/* BASELINE */}

          <div className="panel baseline-panel">

            <div className="panel-header">

              <div>
                <div className="panel-kicker">
                  CALIBRATION
                </div>

                <h2>
                  Machine Baseline
                </h2>
              </div>

              <div
                className={
                  calibrated
                    ? "ready-badge"
                    : "learning-badge"
                }
              >
                {calibrated
                  ? "READY"
                  : "LEARNING"}
              </div>

            </div>


            {calibrated ? (

              <div className="baseline-ready">

                <div className="check-icon">
                  ✓
                </div>

                <div>

                  <strong>
                    Baseline established
                  </strong>

                  <p>
                    MachPulse is now
                    monitoring the machine
                    for abnormal behavior.
                  </p>

                </div>

              </div>

            ) : (

              <div className="calibration-content">

                <div className="calibration-number">
                  {calibrationProgress}
                  <span>
                    /
                    {calibrationTotal}
                  </span>
                </div>

                <div className="calibration-copy">

                  <strong>
                    Learning normal behavior
                  </strong>

                  <p>
                    Collecting healthy
                    vibration windows.
                  </p>

                </div>

                <div className="progress-track">

                  <div
                    className="progress-fill"
                    style={{
                      width:
                        `${calibrationPercent}%`,
                    }}
                  />

                </div>

              </div>

            )}

          </div>

        </section>


        {/* SIGNAL METRICS */}

        <section className="panel">

          <div className="section-heading">

            <div>
              <div className="panel-kicker">
                SIGNAL ANALYSIS
              </div>

              <h2>
                Vibration Features
              </h2>
            </div>

            <div className="live-indicator">
              <span />
              LIVE DATA
            </div>

          </div>


          <div className="metrics-grid">

            <MetricCard
              label="RMS"
              value={formatNumber(
                features.rms,
                3
              )}
              description="Overall vibration intensity"
            />

            <MetricCard
              label="Dominant Frequency"
              value={formatNumber(
                features.dominant_frequency,
                2
              )}
              unit="Hz"
              description="Strongest detected vibration frequency"
            />

            <MetricCard
              label="Std. Deviation"
              value={formatNumber(
                features.std,
                3
              )}
              description="Vibration variability"
            />

            <MetricCard
              label="Crest Factor"
              value={formatNumber(
                features.crest_factor,
                2
              )}
              description="Peak-to-average vibration ratio"
            />

            <MetricCard
              label="Spectral Energy"
              value={formatNumber(
                features.spectral_energy,
                2
              )}
              description="Energy across the frequency spectrum"
            />

            <MetricCard
              label="Anomaly Score"
              value={formatNumber(
                analysis.anomaly_score,
                2
              )}
              description="Deviation from learned baseline"
            />

          </div>

        </section>


        {/* HEALTH TREND */}

        <section className="panel">

          <div className="section-heading">

            <div>
              <div className="panel-kicker">
                MACHINE HISTORY
              </div>

              <h2>
                Health Trend
              </h2>
            </div>

            <div className="trend-current">

              Current health

              <strong>
                {Number.isFinite(
                  health
                )
                  ? Math.round(health)
                  : "--"}
              </strong>

            </div>

          </div>


          <HealthTrend
            history={history}
          />

        </section>


        {/* BOTTOM GRID */}

        <section className="bottom-grid">

          {/* EVENTS */}

          <div className="panel">

            <div className="section-heading">

              <div>
                <div className="panel-kicker">
                  EVENT MONITOR
                </div>

                <h2>
                  Machine Status
                </h2>
              </div>

            </div>


            <div className="event-list">

              <div className="event-item">

                <div className="event-marker success">
                  ✓
                </div>

                <div className="event-content">

                  <strong>
                    Sensor connection
                  </strong>

                  <span>
                    {connected
                      ? "Phone connected and streaming"
                      : "Waiting for sensor connection"}
                  </span>

                </div>

                <time>
                  NOW
                </time>

              </div>


              <div className="event-item">

                <div
                  className={`event-marker ${
                    calibrated
                      ? "success"
                      : "neutral"
                  }`}
                >
                  {calibrated
                    ? "✓"
                    : "·"}
                </div>

                <div className="event-content">

                  <strong>
                    Baseline calibration
                  </strong>

                  <span>
                    {calibrated
                      ? "Baseline established"
                      : `Collecting ${calibrationProgress}/${calibrationTotal} windows`}
                  </span>

                </div>

                <time>
                  LIVE
                </time>

              </div>


              <div className="event-item">

                <div
                  className={`event-marker ${
                    anomaly
                      ? "danger"
                      : "success"
                  }`}
                >
                  {anomaly
                    ? "!"
                    : "✓"}
                </div>

                <div className="event-content">

                  <strong>
                    Anomaly monitor
                  </strong>

                  <span>
                    {anomaly
                      ? "Abnormal vibration detected"
                      : "No active anomaly"}
                  </span>

                </div>

                <time>
                  LIVE
                </time>

              </div>

            </div>

          </div>


          {/* AI */}

          <div className="panel advisor-panel">

            <div className="section-heading">

              <div>

                <div className="panel-kicker">
                  LOCAL AI
                </div>

                <h2>
                  Maintenance Advisor
                </h2>

              </div>

              <div className="ai-badge">
                OLLAMA
              </div>

            </div>


            {data?.ai_advice ? (

              <div className="ai-content">

                <div className="ai-status danger-text">
                  ANOMALY ANALYSIS
                </div>

                <div className="ai-advice">
                  {data.ai_advice}
                </div>

              </div>

            ) : (

              <div className="ai-empty">

                <div className="ai-icon">
                  AI
                </div>

                <div>

                  <strong>
                    No maintenance action
                    required right now.
                  </strong>

                  <p>
                    When the ML system
                    detects a significant
                    anomaly, the local AI
                    advisor will explain
                    what to inspect.
                  </p>

                </div>

              </div>

            )}

          </div>

        </section>


        {/* FOOTER */}

        <footer className="dashboard-footer">

          <div>
            MachPulse • Smartphone-powered
            machine health monitoring
          </div>

          <div>
            Sensor → ML → Insight
          </div>

        </footer>

      </main>

    </div>
  );
}


export default App;