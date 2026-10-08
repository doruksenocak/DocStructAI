import { useState } from 'react'
import './App.css'

function App() {
    const [selectedFile, setSelectedFile] = useState(null)
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)

    async function handleProcess() {
        if (!selectedFile) {
            alert('Please select a file first')
            return
        }

        setResult(null)
        setLoading(true)
        setError(null)

        try {
            const formData = new FormData()
            formData.append('file', selectedFile)

            const response = await fetch('http://localhost:8000/process', {
                method: 'POST',
                body: formData,
            })

            if (!response.ok) {
                throw new Error('Document processing failed')
            }

            const data = await response.json()
            setResult(data)

        } catch (error) {
            setError(error.message)

        } finally {
            setLoading(false)
        }
    }

    return (
        <div>
            <h1>DocStructAI</h1>
            <p>Convert documents into structured data.</p>

            <input
                type="file"
                accept=".pdf,.png,.jpg,.jpeg"
                onChange={(event) => setSelectedFile(event.target.files[0])}
            />

            {selectedFile && (
                <p>Selected: {selectedFile.name}</p>
            )}

            <button
                onClick={handleProcess}
                disabled={loading}
            >
                {loading ? 'Processing...' : 'Process Document'}
            </button>

            {error && (
                <p>{error}</p>
            )}

            {result && (
    <div>
        <h2>Processing Result</h2>

        <p>
            <strong>Filename:</strong> {result.filename}
        </p>

        <p>
            <strong>Validation:</strong>{' '}
            {result.validation.is_valid ? 'Valid ✓' : 'Invalid ✗'}
        </p>

        <h3>Extracted Data</h3>

        <pre>
            {JSON.stringify(result.data, null, 2)}
        </pre>
    </div>
)}
        </div>
    )
}

export default App