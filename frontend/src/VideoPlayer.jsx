export default function VideoPlayer({ jobId }) {
  return (
    <video
      src={`http://localhost:8000/video/${jobId}`}
      controls
      width="100%"
      style={{ marginTop: 16, borderRadius: 8 }}
    />
  )
}