function formatLabel(key) {
  return key
    .replaceAll('_', ' ')
    .replace(/\b\w/g, letter => letter.toUpperCase())
}


function DataDisplay({ data }) {
  return (
    <div className="data-display">

      {Object.entries(data).map(([key, value]) => {

        // ARRAYS
        if (Array.isArray(value)) {

          // Empty array
          if (value.length === 0) {
            return (
              <div className="data-field" key={key}>
                <span className="data-label">
                  {formatLabel(key)}
                </span>

                <strong className="data-value">
                  —
                </strong>
              </div>
            )
          }


          // Simple array: ["Python", "Java", "C++"]
          if (typeof value[0] !== 'object') {
            return (
              <div className="data-list-section" key={key}>

                <span className="data-label">
                  {formatLabel(key)}
                </span>

                <div className="data-chips">
                  {value.map((item, index) => (
                    <span
                      className="data-chip"
                      key={index}
                    >
                      {String(item)}
                    </span>
                  ))}
                </div>

              </div>
            )
          }


          // Array of objects -> table
          const columns = Object.keys(value[0])

          return (
            <div className="data-table-section" key={key}>

              <span className="data-label">
                {formatLabel(key)}
              </span>

              <div className="data-table-wrapper">

                <table className="data-table">

                  <thead>
                    <tr>
                      {columns.map((column) => (
                        <th key={column}>
                          {formatLabel(column)}
                        </th>
                      ))}
                    </tr>
                  </thead>


                  <tbody>

                    {value.map((item, index) => (
                      <tr key={index}>

                        {columns.map((column) => (
                          <td key={column}>

                            {item[column] === null ||
                            item[column] === ''
                              ? '—'
                              : typeof item[column] === 'object'
                                ? JSON.stringify(item[column])
                                : String(item[column])
                            }

                          </td>
                        ))}

                      </tr>
                    ))}

                  </tbody>

                </table>

              </div>

            </div>
          )
        }


        // NESTED OBJECT
        if (typeof value === 'object' && value !== null) {
          return (
            <div
              className="data-list-section"
              key={key}
            >

              <span className="data-label">
                {formatLabel(key)}
              </span>

              <div className="nested-data">
                <DataDisplay data={value} />
              </div>

            </div>
          )
        }


        // SIMPLE VALUE
        return (
          <div className="data-field" key={key}>

            <span className="data-label">
              {formatLabel(key)}
            </span>

            <strong className="data-value">
              {value === null || value === ''
                ? '—'
                : String(value)
              }
            </strong>

          </div>
        )

      })}

    </div>
  )
}


export default DataDisplay