import { useState } from 'react'
import './App.css'

const fileTypes = ['PDF', 'PNG', 'JPG', 'JPEG']
const documentTypes = [
    'CV',
    'Invoice',
    'Receipt',
    'Purchase Order',
    'Contract',
    'Bank Statement'
]

const exportFormats = ['JSON', 'CSV', 'XLSX']

function App() {
    const [selectedFile, setSelectedFile] = useState(null)
    const [result, setResult] = useState(null)
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState(null)
    const [exportFormat, setExportFormat] = useState('json')

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
            formData.append('export_format', exportFormat)

            const response = await fetch('http://localhost:8000/process', {
                method: 'POST',
                body: formData,
            })

            if (!response.ok) {
                throw new Error('Document processing failed')
            }

            const data = await response.json()
            console.log(data)
            setResult(data)

        } catch (error) {
            setError(error.message)

        } finally {
            setLoading(false)
        }
    }

    function handleDownload() {
        if (!result) {
            return
        }

        const url =
            `http://localhost:8000/documents/${result.id}/export?format=${exportFormat}`

        window.location.href = url
    }

    return (
    <div className="app">
        <header className="hero">
            <p className="hero-badge">AI DOCUMENT PROCESSING</p>

            <h1>
                Welcome to <span>DocStructAI</span>
            </h1>

            <p className="hero-description">
                Convert unstructured documents into structured data.
                Upload your document and choose your preferred export format.
            </p>
        </header>

        <h2>Supported Input File Types</h2>

        <div>
            {fileTypes.map((type) => (
                <span key={type}>
                    {type}{' '}
                </span>
            ))}
        </div>

        <h2>Supported Document Types</h2>

        <div>
            {documentTypes.map((type) => (
                <span key={type}>
                    {type}{' '}
                </span>
            ))}
        </div>

        <h2>Choose Export Format</h2>

        <div>
            {exportFormats.map((format) => (
                <button
                    key={format}
                    onClick={() => setExportFormat(format.toLowerCase())}
                >
                    {format}
                </button>
            ))}
        </div>

        <p>Selected format: {exportFormat}</p>

        <h2>Upload Document</h2>

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

                <button onClick={handleDownload}>
                    Download {exportFormat.toUpperCase()}
                </button>

                <pre>
                    {JSON.stringify(result.data, null, 2)}
                </pre>
            </div>
        )}
    </div>
    )
}

export default App