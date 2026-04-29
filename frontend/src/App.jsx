import { useState } from "react";

const API = "http://127.0.0.1:8000";

const SAMPLE_CODE = `def calculate_discount(price, user_type):
    if user_type == "premium":
        if price > 100:
            for i in range(10):
                for j in range(10):
                    price = price * 0.9
    return price`;

export default function App() {
  const [code, setCode] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [tab, setTab] = useState("editor");

  async function analyze() {
    if (!code.trim()) return;
    setLoading(true);
    setError("");
    setResult(null);
    try {
      const res = await fetch(`${API}/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code }),
      });
      if (!res.ok) throw new Error("Analysis failed");
      const data = await res.json();
      setResult(data);
      setTab("results");
    } catch (e) {
      setError("Could not connect to backend. Make sure uvicorn is running.");
    } finally {
      setLoading(false);
    }
  }

  function scoreColor(score) {
    if (score >= 0.7) return "#22c55e";
    if (score >= 0.4) return "#f59e0b";
    return "#ef4444";
  }

  function riskColor(risk) {
    if (risk <= 0.3) return "#22c55e";
    if (risk <= 0.6) return "#f59e0b";
    return "#ef4444";
  }

  function scoreLabel(score) {
    if (score >= 0.7) return "Good";
    if (score >= 0.4) return "Fair";
    return "Poor";
  }

  function riskLabel(risk) {
    if (risk <= 0.3) return "Low Risk";
    if (risk <= 0.6) return "Medium Risk";
    return "High Risk";
  }

  return (
    <div style={styles.root}>
      {/* Header */}
      <header style={styles.header}>
        <div style={styles.headerInner}>
          <div style={styles.logo}>
            <span style={styles.logoIcon}>⬡</span>
            <span style={styles.logoText}>CodeReview<span style={styles.logoAccent}>AI</span></span>
          </div>
          <p style={styles.tagline}>Hybrid static analysis + machine learning</p>
        </div>
      </header>

      <main style={styles.main}>
        {/* Tab bar */}
        <div style={styles.tabs}>
          {["editor", "results"].map((t) => (
            <button
              key={t}
              onClick={() => setTab(t)}
              style={{
                ...styles.tab,
                ...(tab === t ? styles.tabActive : {}),
              }}
            >
              {t === "editor" ? "Code Editor" : `Results ${result ? "✓" : ""}`}
            </button>
          ))}
        </div>

        {/* Editor panel */}
        {tab === "editor" && (
          <div style={styles.panel}>
            <div style={styles.editorHeader}>
              <span style={styles.editorLabel}>Python code</span>
              <button
                style={styles.sampleBtn}
                onClick={() => setCode(SAMPLE_CODE)}
              >
                Load sample
              </button>
            </div>

            <div style={styles.editorWrap}>
              <div style={styles.lineNumbers}>
                {(code || " ").split("\n").map((_, i) => (
                  <div key={i} style={styles.lineNum}>{i + 1}</div>
                ))}
              </div>
              <textarea
                style={styles.editor}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                placeholder="Paste your Python code here..."
                spellCheck={false}
              />
            </div>

            <div style={styles.editorFooter}>
              <span style={styles.charCount}>{code.length} chars · {code.split("\n").length} lines</span>
              <button
                style={{
                  ...styles.analyzeBtn,
                  ...(loading ? styles.analyzeBtnLoading : {}),
                  ...(!code.trim() ? styles.analyzeBtnDisabled : {}),
                }}
                onClick={analyze}
                disabled={loading || !code.trim()}
              >
                {loading ? (
                  <span style={styles.spinner}>⟳ Analyzing...</span>
                ) : (
                  "Analyze Code →"
                )}
              </button>
            </div>

            {error && <div style={styles.error}>{error}</div>}
          </div>
        )}

        {/* Results panel */}
        {tab === "results" && (
          <div style={styles.panel}>
            {!result ? (
              <div style={styles.empty}>
                <div style={styles.emptyIcon}>◎</div>
                <p style={styles.emptyText}>No results yet. Analyze some code first.</p>
                <button style={styles.goBtn} onClick={() => setTab("editor")}>
                  Go to editor
                </button>
              </div>
            ) : (
              <div>
                {/* Score cards */}
                <div style={styles.scoreRow}>
                  <div style={styles.scoreCard}>
                    <div style={styles.scoreLabel}>Quality Score</div>
                    <div style={{ ...styles.scoreBig, color: scoreColor(result.quality_score) }}>
                      {Math.round(result.quality_score * 100)}
                      <span style={styles.scoreUnit}>/100</span>
                    </div>
                    <div style={{ ...styles.scoreBadge, background: scoreColor(result.quality_score) + "22", color: scoreColor(result.quality_score) }}>
                      {scoreLabel(result.quality_score)}
                    </div>
                  </div>

                  <div style={styles.scoreCard}>
                    <div style={styles.scoreLabel}>Bug Risk</div>
                    <div style={{ ...styles.scoreBig, color: riskColor(result.bug_risk) }}>
                      {Math.round(result.bug_risk * 100)}
                      <span style={styles.scoreUnit}>%</span>
                    </div>
                    <div style={{ ...styles.scoreBadge, background: riskColor(result.bug_risk) + "22", color: riskColor(result.bug_risk) }}>
                      {riskLabel(result.bug_risk)}
                    </div>
                  </div>

                  <div style={styles.scoreCard}>
                    <div style={styles.scoreLabel}>Issues Found</div>
                    <div style={{ ...styles.scoreBig, color: result.issues.length > 3 ? "#ef4444" : "#f59e0b" }}>
                      {result.issues.length}
                    </div>
                    <div style={{ ...styles.scoreBadge, background: "#f59e0b22", color: "#f59e0b" }}>
                      detected
                    </div>
                  </div>
                </div>

                {/* Issues */}
                {result.issues.length > 0 && (
                  <div style={styles.section}>
                    <div style={styles.sectionTitle}>
                      <span style={{ color: "#ef4444" }}>✗</span> Issues
                    </div>
                    {result.issues.map((issue, i) => (
                      <div key={i} style={styles.issueItem}>
                        <span style={styles.issueDot} />
                        {issue}
                      </div>
                    ))}
                  </div>
                )}

                {/* Suggestions */}
                {result.suggestions.length > 0 && (
                  <div style={styles.section}>
                    <div style={styles.sectionTitle}>
                      <span style={{ color: "#22c55e" }}>✓</span> Suggestions
                    </div>
                    {result.suggestions.map((s, i) => (
                      <div key={i} style={styles.suggItem}>
                        <span style={styles.suggIcon}>→</span>
                        {s}
                      </div>
                    ))}
                  </div>
                )}

                {/* Features */}
                <div style={styles.section}>
                  <div style={styles.sectionTitle}>◈ Code Metrics</div>
                  <div style={styles.metricsGrid}>
                    {Object.entries(result.features).map(([k, v]) => (
                      <div key={k} style={styles.metricItem}>
                        <div style={styles.metricKey}>{k.replace(/_/g, " ")}</div>
                        <div style={styles.metricVal}>{v}</div>
                      </div>
                    ))}
                  </div>
                </div>

                <button style={styles.reanalyzeBtn} onClick={() => setTab("editor")}>
                  ← Analyze another
                </button>
              </div>
            )}
          </div>
        )}
      </main>
    </div>
  );
}

const styles = {
  root: {
    minHeight: "100vh",
    background: "#0a0a0f",
    color: "#e2e8f0",
    fontFamily: "'JetBrains Mono', 'Fira Code', 'Courier New', monospace",
  },
  header: {
    borderBottom: "1px solid #1e293b",
    padding: "20px 0",
    background: "#0d0d14",
  },
  headerInner: {
    maxWidth: 900,
    margin: "0 auto",
    padding: "0 24px",
    display: "flex",
    alignItems: "center",
    gap: 20,
  },
  logo: {
    display: "flex",
    alignItems: "center",
    gap: 10,
  },
  logoIcon: {
    fontSize: 24,
    color: "#6366f1",
  },
  logoText: {
    fontSize: 20,
    fontWeight: 700,
    letterSpacing: "-0.5px",
    color: "#f1f5f9",
  },
  logoAccent: {
    color: "#6366f1",
  },
  tagline: {
    margin: 0,
    fontSize: 12,
    color: "#475569",
    borderLeft: "1px solid #1e293b",
    paddingLeft: 20,
  },
  main: {
    maxWidth: 900,
    margin: "0 auto",
    padding: "32px 24px",
  },
  tabs: {
    display: "flex",
    gap: 4,
    marginBottom: 24,
    background: "#111118",
    borderRadius: 10,
    padding: 4,
    border: "1px solid #1e293b",
    width: "fit-content",
  },
  tab: {
    padding: "8px 20px",
    borderRadius: 7,
    border: "none",
    background: "transparent",
    color: "#64748b",
    cursor: "pointer",
    fontSize: 13,
    fontFamily: "inherit",
    fontWeight: 500,
    transition: "all 0.15s",
  },
  tabActive: {
    background: "#1e293b",
    color: "#e2e8f0",
  },
  panel: {
    background: "#0d0d14",
    borderRadius: 12,
    border: "1px solid #1e293b",
    overflow: "hidden",
  },
  editorHeader: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "14px 20px",
    borderBottom: "1px solid #1e293b",
    background: "#111118",
  },
  editorLabel: {
    fontSize: 12,
    color: "#64748b",
    textTransform: "uppercase",
    letterSpacing: "0.08em",
  },
  sampleBtn: {
    fontSize: 12,
    padding: "4px 12px",
    background: "transparent",
    border: "1px solid #334155",
    borderRadius: 6,
    color: "#94a3b8",
    cursor: "pointer",
    fontFamily: "inherit",
  },
  editorWrap: {
    display: "flex",
    minHeight: 300,
  },
  lineNumbers: {
    padding: "16px 12px",
    background: "#090910",
    borderRight: "1px solid #1e293b",
    minWidth: 44,
    textAlign: "right",
    userSelect: "none",
  },
  lineNum: {
    fontSize: 13,
    lineHeight: "1.7",
    color: "#334155",
  },
  editor: {
    flex: 1,
    padding: "16px 20px",
    background: "transparent",
    border: "none",
    outline: "none",
    color: "#e2e8f0",
    fontSize: 13,
    lineHeight: "1.7",
    fontFamily: "inherit",
    resize: "none",
    minHeight: 300,
  },
  editorFooter: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "14px 20px",
    borderTop: "1px solid #1e293b",
    background: "#111118",
  },
  charCount: {
    fontSize: 12,
    color: "#475569",
  },
  analyzeBtn: {
    padding: "10px 28px",
    background: "#6366f1",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    fontSize: 13,
    fontWeight: 600,
    fontFamily: "inherit",
    cursor: "pointer",
    letterSpacing: "0.02em",
  },
  analyzeBtnLoading: {
    background: "#4338ca",
    cursor: "wait",
  },
  analyzeBtnDisabled: {
    background: "#1e293b",
    color: "#475569",
    cursor: "not-allowed",
  },
  spinner: {
    display: "inline-block",
    animation: "spin 1s linear infinite",
  },
  error: {
    margin: 16,
    padding: "12px 16px",
    background: "#ef444422",
    border: "1px solid #ef444444",
    borderRadius: 8,
    fontSize: 13,
    color: "#fca5a5",
  },
  empty: {
    padding: "80px 20px",
    textAlign: "center",
  },
  emptyIcon: {
    fontSize: 48,
    color: "#1e293b",
    marginBottom: 16,
  },
  emptyText: {
    color: "#475569",
    fontSize: 14,
    marginBottom: 20,
  },
  goBtn: {
    padding: "10px 24px",
    background: "#6366f1",
    color: "#fff",
    border: "none",
    borderRadius: 8,
    fontSize: 13,
    fontFamily: "inherit",
    cursor: "pointer",
  },
  scoreRow: {
    display: "flex",
    gap: 0,
    borderBottom: "1px solid #1e293b",
  },
  scoreCard: {
    flex: 1,
    padding: "28px 24px",
    textAlign: "center",
    borderRight: "1px solid #1e293b",
  },
  scoreLabel: {
    fontSize: 11,
    color: "#64748b",
    textTransform: "uppercase",
    letterSpacing: "0.1em",
    marginBottom: 8,
  },
  scoreBig: {
    fontSize: 48,
    fontWeight: 700,
    lineHeight: 1,
    marginBottom: 10,
  },
  scoreUnit: {
    fontSize: 18,
    fontWeight: 400,
    color: "#475569",
  },
  scoreBadge: {
    display: "inline-block",
    fontSize: 11,
    padding: "3px 10px",
    borderRadius: 20,
    fontWeight: 600,
    letterSpacing: "0.05em",
  },
  section: {
    padding: "20px 24px",
    borderBottom: "1px solid #1e293b",
  },
  sectionTitle: {
    fontSize: 12,
    textTransform: "uppercase",
    letterSpacing: "0.1em",
    color: "#64748b",
    marginBottom: 14,
    display: "flex",
    alignItems: "center",
    gap: 8,
  },
  issueItem: {
    display: "flex",
    alignItems: "flex-start",
    gap: 10,
    fontSize: 13,
    color: "#cbd5e1",
    padding: "7px 0",
    borderBottom: "1px solid #0f172a",
  },
  issueDot: {
    width: 6,
    height: 6,
    borderRadius: "50%",
    background: "#ef4444",
    marginTop: 5,
    flexShrink: 0,
  },
  suggItem: {
    display: "flex",
    alignItems: "flex-start",
    gap: 10,
    fontSize: 13,
    color: "#cbd5e1",
    padding: "7px 0",
    borderBottom: "1px solid #0f172a",
  },
  suggIcon: {
    color: "#22c55e",
    flexShrink: 0,
    fontWeight: 700,
  },
  metricsGrid: {
    display: "grid",
    gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))",
    gap: 8,
  },
  metricItem: {
    background: "#111118",
    border: "1px solid #1e293b",
    borderRadius: 8,
    padding: "10px 14px",
  },
  metricKey: {
    fontSize: 11,
    color: "#475569",
    marginBottom: 4,
    textTransform: "capitalize",
  },
  metricVal: {
    fontSize: 18,
    fontWeight: 700,
    color: "#6366f1",
  },
  reanalyzeBtn: {
    margin: 20,
    padding: "10px 20px",
    background: "transparent",
    border: "1px solid #334155",
    borderRadius: 8,
    color: "#94a3b8",
    cursor: "pointer",
    fontSize: 13,
    fontFamily: "inherit",
  },
};