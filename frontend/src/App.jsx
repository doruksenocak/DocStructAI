import { useEffect, useState } from 'react'

import {
  FileText,
  Image,
  UserRound,
  ReceiptText,
  Receipt,
  PackageCheck,
  FileSignature,
  Landmark,
  Braces,
  Table,
  FileSpreadsheet,
  CloudUpload,
  Sparkles,
  CircleCheck,
  Download
} from 'lucide-react'

import './App.css'
import DataDisplay from './DataDisplay'


const fileTypes = ['PDF', 'PNG', 'JPG', 'JPEG']


const documentTypes = [
  { name: 'CV', icon: UserRound },
  { name: 'Invoice', icon: ReceiptText },
  { name: 'Receipt', icon: Receipt },
  { name: 'Purchase Order', icon: PackageCheck },
  { name: 'Contract', icon: FileSignature },
  { name: 'Bank Statement', icon: Landmark }
]


const exportFormats = [
  { name: 'JSON', icon: Braces },
  { name: 'CSV', icon: Table },
  { name: 'XLSX', icon: FileSpreadsheet }
]


function App() {

  const [selectedFile, setSelectedFile] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [exportFormat, setExportFormat] = useState(null)

  const [documents, setDocuments] = useState([])


  useEffect(() => {

    async function loadDocuments() {
      try {
        const response = await fetch(
          'http://localhost:8000/documents'
        )

        if (!response.ok) {
          throw new Error(
            'Could not load document history'
          )
        }

        const data = await response.json()

        setDocuments(data)

      } catch (error) {
        console.error(error)
      }
    }

    loadDocuments()

  }, [])


  async function handleProcess() {

    if (!selectedFile && !exportFormat) {
      setError(
        'Please select a document and an export format.'
      )
      return
    }

    if (!selectedFile) {
      setError('Please select a document.')
      return
    }

    if (!exportFormat) {
      setError('Please select an export format.')
      return
    }

    setResult(null)
    setLoading(true)
    setError(null)

    try {

      const formData = new FormData()

      formData.append('file', selectedFile)
      formData.append('export_format', exportFormat)

      const response = await fetch(
        'http://localhost:8000/process',
        {
          method: 'POST',
          body: formData,
        }
      )

      if (!response.ok) {
        throw new Error(
          'Document processing failed'
        )
      }

      const data = await response.json()

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


      {/* HERO */}

      <header className="hero">

        <p className="hero-badge">
          AI DOCUMENT PROCESSING
        </p>

        <h1>
          Welcome to <span>DocStructAI</span>
        </h1>

        <p className="hero-description">
          Convert unstructured documents into structured data.
          Upload your document and choose your preferred export format.
        </p>

      </header>



      {/* INPUT FILE TYPES */}

      <section className="section">

        <div className="section-heading">

          <p className="section-label">
            INPUT
          </p>

          <h2>
            Supported Input File Types
          </h2>

          <p>
            Upload PDFs or common image formats.
          </p>

        </div>


        <div className="file-type-grid">

          {fileTypes.map((type) => (

            <div
              className="info-card"
              key={type}
            >

              <div className="card-icon">

                {type === 'PDF'
                  ? <FileText size={28} />
                  : <Image size={28} />
                }

              </div>

              <span>
                {type}
              </span>

            </div>

          ))}

        </div>

      </section>



      {/* DOCUMENT TYPES */}

      <section className="section">

        <div className="section-heading">

          <p className="section-label">
            DOCUMENTS
          </p>

          <h2>
            Supported Document Types
          </h2>

          <p>
            DocStructAI automatically detects the type of document you upload.
          </p>

        </div>


        <div className="document-grid">

          {documentTypes.map((type) => {

            const Icon = type.icon

            return (

              <div
                className="info-card"
                key={type.name}
              >

                <div className="card-icon">
                  <Icon size={28} />
                </div>

                <span>
                  {type.name}
                </span>

              </div>

            )
          })}

        </div>

      </section>



      {/* EXPORT FORMAT */}

      <section className="section">

        <div className="section-heading">

          <p className="section-label">
            EXPORT
          </p>

          <h2>
            Choose Export Format
          </h2>

          <p>
            Choose how you want to download your structured document.
          </p>

        </div>


        <div className="export-grid">

          {exportFormats.map((format) => {

            const Icon = format.icon

            const selected =
              exportFormat ===
              format.name.toLowerCase()

            return (

              <button
                className={
                  selected
                    ? 'export-card selected'
                    : 'export-card'
                }
                key={format.name}
                onClick={() => {
                  setExportFormat(
                    format.name.toLowerCase()
                  )
                  setError(null)
                }}
              >

                <div className="export-icon">
                  <Icon size={30} />
                </div>


                <div>

                  <strong>
                    {format.name}
                  </strong>

                  <span>

                    {format.name === 'JSON' &&
                      'Structured data'}

                    {format.name === 'CSV' &&
                      'Spreadsheet tables'}

                    {format.name === 'XLSX' &&
                      'Excel workbook'}

                  </span>

                </div>


                {selected && (

                  <CircleCheck
                    className="selected-check"
                    size={21}
                  />

                )}

              </button>

            )
          })}

        </div>

      </section>



      {/* UPLOAD */}

      <section className="section">

        <div className="section-heading">

          <p className="section-label">
            UPLOAD
          </p>

          <h2>
            Upload Document
          </h2>

          <p>
            Select a supported document and let DocStructAI process it.
          </p>

        </div>


        <label className="upload-area">

          <CloudUpload
            className="upload-icon"
            size={42}
          />

          <strong>

            {selectedFile
              ? selectedFile.name
              : 'Choose a document'
            }

          </strong>


          <span>

            {selectedFile
              ? 'Document ready to process'
              : 'PDF, PNG, JPG or JPEG'
            }

          </span>


          <input
            type="file"
            accept=".pdf,.png,.jpg,.jpeg"
            onChange={(event) => {

              setSelectedFile(
                event.target.files[0]
              )

              setError(null)

            }}
          />

        </label>


        <button
          className="process-button"
          onClick={handleProcess}
          disabled={loading}
        >

          <Sparkles size={20} />

          {loading
            ? 'Processing...'
            : 'Process Document'
          }

        </button>


        {error && (

          <div className="error-message">
            {error}
          </div>

        )}

      </section>



      {/* PROCESSING RESULT */}

      {result && (

        <section className="result-section">

          <div className="result-header">


            <div>

              <p className="section-label">
                RESULT
              </p>

              <h2>
                Processing Result
              </h2>

            </div>


            <div className="result-actions">


              <div
                className={
                  result.validation.is_valid
                    ? 'validation valid'
                    : 'validation invalid'
                }
              >

                <CircleCheck size={18} />

                {result.validation.is_valid
                  ? 'Valid'
                  : 'Invalid'
                }

              </div>


              <button
                className="download-button"
                onClick={handleDownload}
              >

                <Download size={19} />

                Download {
                  exportFormat.toUpperCase()
                }

              </button>


            </div>

          </div>



          {/* RESULT SUMMARY */}

          <div className="result-summary">

            <div>

              <span>
                Filename
              </span>

              <strong>
                {result.filename}
              </strong>

            </div>


            <div>

              <span>
                Detected Type
              </span>

              <strong>
                {result.document_type}
              </strong>

            </div>


            <div>

              <span>
                Export Format
              </span>

              <strong>
                {exportFormat.toUpperCase()}
              </strong>

            </div>

          </div>



          {/* EXTRACTED DATA */}

          <div className="result-data">

            <div className="result-data-header">

              <h3>
                Extracted Data
              </h3>

              <span>
                Structured output
              </span>

            </div>


            <DataDisplay
              data={result.data}
            />

          </div>


        </section>

      )}



      {/* DOCUMENT HISTORY */}

      <section className="section">

        <div className="section-heading">

          <p className="section-label">
            HISTORY
          </p>

          <h2>
            Processed Documents
          </h2>

          <p>
            Your previously processed documents.
          </p>

        </div>


        <div className="document-history">

          {documents.map((document) => (

            <div
              className="history-item"
              key={document.id}
            >

              <div>

                <strong>
                  {document.filename}
                </strong>

                <span>
                  {document.document_type}
                </span>

              </div>

            </div>

          ))}

        </div>

      </section>


    </div>

  )
}


export default App