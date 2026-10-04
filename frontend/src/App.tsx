import { useState } from 'react';
import {
  LiveKitRoom,
  RoomAudioRenderer,
  ControlBar,
  BarVisualizer,
  useVoiceAssistant,
} from '@livekit/components-react';
import '@livekit/components-styles';

const FIXED_TOPIC = 'Car Rental Service';

export default function App() {
  const [token, setToken] = useState<string | null>(null);
  const [url, setUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleConnect = async () => {
    setLoading(true);
    try {
      const res = await fetch('http://127.0.0.1:8000/api/token', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic: FIXED_TOPIC,
          participant_name: 'Tester',
        }),
      });
      if (!res.ok) throw new Error('Server error while generating token');
      const data = await res.json();
      setUrl(data.server_url);
      setToken(data.participant_token);
    } catch (err) {
      alert(err);
    } finally {
      setLoading(false);
    }
  };

  if (!token || !url) {
    return (
      <div style={{ padding: 40, fontFamily: 'sans-serif', textAlign: 'center', color: '#fff' }}>
        <h2>Voice Agent Testing</h2>
        <p style={{ color: '#aaa', marginBottom: 25 }}>
          Call topic: <b>{FIXED_TOPIC}</b>
        </p>
        <button
          onClick={handleConnect}
          disabled={loading}
          style={{ padding: '12px 28px', fontSize: 16, cursor: 'pointer', borderRadius: 6 }}
        >
          {loading ? 'Connecting...' : 'Connect to Agent'}
        </button>
      </div>
    );
  }

  return (
    <LiveKitRoom
      serverUrl={url}
      token={token}
      connect={true}
      audio={true}
      video={false}
      data-lk-theme="default"
      onDisconnected={() => {
        setToken(null);
        setUrl(null);
      }}
      style={{ height: '100vh', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}
    >
      <AgentVisualizer topic={FIXED_TOPIC} />
      <ControlBar controls={{ microphone: true, camera: false, screenShare: false }} />
      <RoomAudioRenderer />
    </LiveKitRoom>
  );
}

function AgentVisualizer({ topic }: { topic: string }) {
  const { state, audioTrack } = useVoiceAssistant();

  return (
    <div style={{ textAlign: 'center', marginBottom: 30, color: '#fff' }}>
      <h3>Topic: {topic}</h3>
      <p>Agent status: <b>{state}</b></p>
      <div style={{ width: 300, height: 100, margin: '0 auto' }}>
        <BarVisualizer state={state} trackRef={audioTrack} barCount={7} />
      </div>
    </div>
  );
}