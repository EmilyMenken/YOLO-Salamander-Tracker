import { useState, useEffect, useRef } from "react"
import VideoPlayer from "./VideoPlayer"
import MetricsPanel from "./MetricsPanel"

export default function Home() {
  const [jobId, setJobId] = useState(null)
  const [metrics, setMetrics] = useState(null)
  const [loading, setLoading] = useState(false)
  const [dots, setDots] = useState(0)
  const [progress, setProgress] = useState(0)
  const progressInterval = useRef(null)

  useEffect(() => {
    if (!loading) return
    const interval = setInterval(() => {
      setDots(d => d === 3 ? 0 : d + 1)
    }, 500)
    return () => clearInterval(interval)
  }, [loading])

  useEffect(() => {
    if (!loading) {
      clearInterval(progressInterval.current)
      return
    }
    progressInterval.current = setInterval(async () => {
      try {
        const res = await fetch("http://localhost:8000/progress")
        const data = await res.json()
        setProgress(data.progress)
      } catch {
        // if the backend isn't ready yet
      }
    }, 1000)
    return () => clearInterval(progressInterval.current)
  }, [loading])

  async function handleUpload(e) {
    const file = e.target.files[0]
    if (!file) return
    setLoading(true)
    setProgress(0)
    setJobId(null)
    setMetrics(null)

    const form = new FormData()
    form.append("file", file)

    const res = await fetch("http://localhost:8000/upload", {
      method: "POST",
      body: form,
    })
    const data = await res.json()
    setJobId(data.job_id)
    setMetrics(data.metrics)
    setProgress(100)
    setLoading(false)
  }

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: 24 }}>
      <h1>Salamander Tracker</h1>
      <p>Upload a video to detect and track salamanders using YOLO.</p>

      <input 
        type="file" 
        accept="video/*" 
        onChange={handleUpload}
        disabled={loading}
        style={{ cursor: loading ? "not-allowed" : "pointer" }}
        />

    {loading && (
        <div style={{ marginTop: 16 }}>
        <p>Processing video{".".repeat(dots)}</p>
        <p style={{ fontSize: 14, color: "#aaa" }}>This may take a moment, please don't refresh the tab!</p>
        <div style={{
        width: "100%",
        backgroundColor: "#ddd",
        borderRadius: 8,
        height: 20,
        overflow: "hidden"
        }}>
        <div style={{
            width: `${progress}%`,
            backgroundColor: "#4caf50",
            height: "100%",
            borderRadius: 8,
            transition: "width 0.5s ease"
        }} />
        </div>
        <p style={{ fontSize: 14, color: "#555" }}>{Math.round(progress)}%</p>
    </div>
    )}

      {jobId && !loading && (
  <>
    <p style={{ marginTop: 16, color: "#4caf50", fontWeight: "bold" }}>
      Completed! Thank you for your patience.
    </p>
    <VideoPlayer jobId={jobId} />
    <MetricsPanel metrics={metrics} />
  </>
)}
    </div>
  )
}