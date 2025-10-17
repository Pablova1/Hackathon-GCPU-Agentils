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

  const handleAlimentChange = (index, field, value) => {
    const updatedAliments = [...response.aliments];
    updatedAliments[index][field] = value;
    setResponse({ ...response, aliments: updatedAliments });
  };

  const handleAddAliment = () => {
    const newAliment = { nom: '', quantite_estimee: 0 };
    setResponse({ ...response, aliments: [...response.aliments, newAliment] });
  };

  const handleDeleteAliment = (index) => {
    const updatedAliments = response.aliments.filter((_, i) => i !== index);
    setResponse({ ...response, aliments: updatedAliments });
  };

  const handleValidateAliments = async () => {
    if (!response || !response.aliments) {
      setError('No aliments to validate.');
      return;
    }

    try {
      const res = await fetch('http://localhost:8000/api/analyze/nutrients', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(response.aliments), // Send the list of aliments directly
      });

      if (!res.ok) {
        throw new Error(`HTTP error! status: ${res.status}`);
      }

      const data = await res.json();
      console.log('Nutrient analysis result:', data);
      alert('Nutrient analysis completed! Check the console for details.');
      setError(null);
    } catch (err) {
      setError(err.message);
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
              <li key={index}>
                <input
                  type="text"
                  value={aliment.name}
                  onChange={(e) => handleAlimentChange(index, 'name', e.target.value)}
                  placeholder="Nom de l'aliment"
                />
                <input
                  type="number"
                  value={aliment.estimated_quantity}
                  onChange={(e) => handleAlimentChange(index, 'estimated_quantity', parseInt(e.target.value, 10))}
                  placeholder="Quantité"
                />
                <button onClick={() => handleDeleteAliment(index)}>Delete</button>
              </li>
            ))}
          </ul>
          <button onClick={handleAddAliment}>Add Aliment</button>
          <button onClick={handleValidateAliments}>Validate Aliments</button>
        </div>
      )}
    </div>
  );
}