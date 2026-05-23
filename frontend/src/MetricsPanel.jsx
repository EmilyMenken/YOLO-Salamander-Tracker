export default function MetricsPanel({ metrics }) {
  if (!metrics) return null
  const { detection_counts, time_on_screen, total_distance_px, fps } = metrics

  return (
    <div style={{ marginTop: 20 }}>
      <h2>Metrics</h2>

      <h3>Time on Screen</h3>
      <ul>
        {Object.entries(time_on_screen).map(([id, frames]) => (
          <li key={id}>
            Salamander {id}: {frames} frames ({(frames / fps).toFixed(1)}s)
          </li>
        ))}
      </ul>

      <h3>Total Distance Traveled (pixels)</h3>
      <ul>
        {Object.entries(total_distance_px).map(([id, dist]) => (
          <li key={id}>Salamander {id}: {dist} px</li>
        ))}
      </ul>

      <h3>Peak Detections in a Single Frame</h3>
      <p>{Math.max(...detection_counts)} salamander(s)</p>
    </div>
  )
}