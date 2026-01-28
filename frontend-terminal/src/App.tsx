import { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import axios from 'axios';
import { ScanFace, UserCheck, XCircle, AlertTriangle } from 'lucide-react';

export default function App() {
    const webcamRef = useRef<Webcam>(null);
    const [empIdInput, setEmpIdInput] = useState('');
    const [status, setStatus] = useState<'idle' | 'processing' | 'success' | 'failed'>('idle');
    const [result, setResult] = useState<any>(null);
    const [currentTime, setCurrentTime] = useState(new Date());
    const [camError, setCamError] = useState<string | null>(null);

    // Update clock
    useEffect(() => {
        const timer = setInterval(() => setCurrentTime(new Date()), 1000);
        return () => clearInterval(timer);
    }, []);

    // Auto-reset status
    useEffect(() => {
        if (status === 'success' || status === 'failed') {
            const timer = setTimeout(() => {
                setStatus('idle');
                setResult(null);
                setEmpIdInput('');
            }, 4000);
            return () => clearTimeout(timer);
        }
    }, [status]);

    const verifyFile = async (file: File) => {
        // If ID is empty, we do 1:N search
        setStatus('processing');
        const formData = new FormData();
        if (empIdInput.trim()) {
            formData.append('emp_id', empIdInput);
        }
        formData.append('file', file);

        try {
            const response = await axios.post('/api/v1/attendance/mark', formData);
            if (response.data.status === 'success') {
                setResult(response.data);
                setStatus('success');
            } else {
                setResult(response.data);
                setStatus('failed');
            }
        } catch (error: any) {
            console.error(error);
            setResult({ reason: error.response?.data?.detail || "Network Error: Check backend connection" });
            setStatus('failed');
        }
    };

    const captureAndVerify = useCallback(async () => {
        if (camError) {
            alert("Camera not working. Please use the 'Upload Photo' button if visible.");
            return;
        }

        if (!webcamRef.current) {
            return;
        }

        setStatus('processing');
        const imageSrc = webcamRef.current.getScreenshot();

        if (!imageSrc) {
            setResult({ reason: "Camera capture failed. Ensure camera permissions are granted." });
            setStatus('failed');
            return;
        }

        // Convert base64 to blob
        const res = await fetch(imageSrc);
        const blob = await res.blob();
        const file = new File([blob], "attendance_capture.jpg", { type: "image/jpeg" });

        await verifyFile(file);

    }, [webcamRef, empIdInput, camError]);

    return (
        <div className="terminal-container">
            <div className="clock">
                {currentTime.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
            </div>

            <h1 style={{ fontSize: '2rem', marginBottom: '0.5rem' }}>Attendance Terminal</h1>
            <p style={{ opacity: 0.6, marginBottom: '2rem' }}>Look directly at the camera</p>

            {/* Camera View */}
            <div className="camera-frame">
                {!camError ? (
                    <Webcam
                        audio={false}
                        ref={webcamRef}
                        screenshotFormat="image/jpeg"
                        // videoConstraints={{ facingMode: "user" }} // Removed strict constraint
                        style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                        onUserMediaError={(err) => {
                            console.error("Webcam Error:", err);
                            const msg = typeof err === 'string' ? err : err.message || err.name;
                            if (msg.includes("Permission") || msg.includes("NotAllowed")) {
                                setCamError("Permission Denied. Click the lock icon in URL bar to explicitly allow Camera.");
                            } else {
                                setCamError("Camera Error: " + msg + ". Check if camera is connected.");
                            }
                        }}
                    />
                ) : (
                    <div style={{ padding: '2rem', textAlign: 'center', color: '#ef4444', display: 'flex', flexDirection: 'column', gap: '1rem', alignItems: 'center' }}>
                        <AlertTriangle size={48} />
                        <h3>Camera Unavailable</h3>
                        <p style={{ maxWidth: '300px', fontSize: '0.9rem' }}>{camError}</p>

                        <div style={{ display: 'flex', gap: '1rem' }}>
                            <button
                                onClick={() => window.location.reload()}
                                style={{ padding: '0.5rem 1rem', borderRadius: '8px', border: '1px solid currentColor', background: 'transparent', color: 'inherit', cursor: 'pointer' }}
                            >
                                Retry
                            </button>

                            <label style={{ padding: '0.5rem 1rem', borderRadius: '8px', background: '#3b82f6', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                                <span>Upload Photo</span>
                                <input
                                    type="file"
                                    accept="image/*"
                                    hidden
                                    onChange={(e) => {
                                        const file = e.target.files?.[0];
                                        if (file) {
                                            // Trigger verify directly with file
                                            verifyFile(file);
                                        }
                                    }}
                                />
                            </label>
                        </div>
                    </div>
                )}

                {status === 'processing' && (
                    <div className="camera-overlay">
                        <div className="scan-line"></div>
                        <div style={{ marginTop: '1rem', fontWeight: 600 }}>
                            {empIdInput ? 'Verifying ID...' : 'Identifying Face...'}
                        </div>
                    </div>
                )}

                {status === 'success' && (
                    <div className="camera-overlay" style={{ background: 'rgba(34, 197, 94, 0.9)', color: 'white', flexDirection: 'column' }}>
                        <UserCheck size={64} />
                        <h2>Verified</h2>
                    </div>
                )}

                {status === 'failed' && (
                    <div className="camera-overlay" style={{ background: 'rgba(239, 68, 68, 0.9)', color: 'white', flexDirection: 'column' }}>
                        <XCircle size={64} />
                        <h2>Failed</h2>
                        <p style={{ marginTop: '1rem', fontSize: '1rem', padding: '0 2rem', textAlign: 'center' }}>
                            {result?.reason || "Unknown Error"}
                        </p>
                    </div>
                )}
            </div>

            {/* Interact Section */}
            <div style={{ width: '100%', maxWidth: '600px', display: 'flex', gap: '1rem', flexDirection: 'column' }}>
                <input
                    type="text"
                    placeholder="Auto-Detect (Or enter ID)"
                    value={empIdInput}
                    onChange={(e) => setEmpIdInput(e.target.value)}
                    style={{
                        padding: '1rem',
                        fontSize: '1.2rem',
                        borderRadius: '8px',
                        border: '1px solid #334155',
                        background: '#1e293b',
                        color: 'white',
                        textAlign: 'center'
                    }}
                />

                <button
                    className="btn-large"
                    onClick={captureAndVerify}
                    disabled={status === 'processing' || !!camError}
                    style={{ justifyContent: 'center', width: '100%', opacity: camError ? 0.5 : 1 }}
                >
                    <ScanFace size={24} />
                    {status === 'processing' ? 'Scanning...' : (empIdInput ? 'Verify ID' : 'Scan Face')}
                </button>
            </div>
        </div>
    )
}
