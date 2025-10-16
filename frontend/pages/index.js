import { useState } from 'react';

export default function Home() {
  const [file, setFile] = useState(null);
  const [response, setResponse] = useState(null);
  const [error, setError] = useState(null);

  const handleFileChange = (event) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    if (!file) {
      setError('Please upload an image.');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('http://localhost:8000/api/analyze/plate', {
        method: 'POST',
        body: formData,
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      setResponse(data);
      setError(null);
    } catch (err) {
      setError(err.message);
      setResponse(null);
    }
  };

  return (
    <div style={{ fontFamily: 'Arial, sans-serif', padding: '20px' }}>
      <h1>Food Analyzer</h1>
      <form onSubmit={handleSubmit}>
        <div>
          <label htmlFor="file">Upload an image of your plate:</label>
          <input type="file" id="file" accept="image/*" onChange={handleFileChange} />
        </div>
        <button type="submit">Analyze</button>
      </form>

      {error && <p style={{ color: 'red' }}>{error}</p>}

      {response && (
        <div>
          <h2>Analysis Result</h2>
          <p>{response.message}</p>
          <ul>
            {response.aliments.map((aliment, index) => (
              <li key={index}>{aliment.nom} - {aliment.quantite_estimee}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}