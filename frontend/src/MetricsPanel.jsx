export default function MetricsPanel({ metrics }) {
  if (!metrics) return null
const {
  detection_counts,
  time_on_screen,
  total_distance_px,
  average_distance_px,
  fps
} = metrics

  return (
    <div style={{ marginTop: 20 }}>
      <h2>Metrics</h2>

      <h3>Per Salamander</h3>
      <table style={{ width: "100%", borderCollapse: "collapse", marginBottom: 24 }}>
        <thead>
          <tr>
            <th style={th}>Track ID</th>
            <th style={th}>Label</th>
            <th style={th}>Time on Screen</th>
            <th style={th}>Distance Traveled</th>
          </tr>
        </thead>
        <tbody>
          {Object.entries(time_on_screen).map(([id, frames]) => (
            <tr key={id}>
              <td style={td}>{id}</td>
              <td style={td}>salamander</td>
              <td style={td}>{frames} frames ({(frames / fps).toFixed(1)}s)</td>
              <td style={td}>{total_distance_px[id] ?? 0} px</td>
            </tr>
          ))}
        </tbody>
      </table>

      <h3>Peak Detections in a Single Frame</h3>
      <p>{Math.max(...detection_counts)} salamander(s)</p>
      <h3>Average Distance Traveled</h3>
      <p>{average_distance_px} px</p>
    </div>
  )
}

const th = {
  textAlign: "left",
  padding: "8px 12px",
  borderBottom: "2px solid #444",
  color: "#aaa",
  fontSize: 14,
}

const td = {
  padding: "8px 12px",
  borderBottom: "1px solid #333",
  fontSize: 14,
}