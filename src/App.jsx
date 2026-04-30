import React, { useState } from 'react';
import './index.css';

function App() {
  const [story, setStory] = useState('');
  const [isForging, setIsForging] = useState(false);
  const [status, setStatus] = useState('');

  const handleForge = () => {
    if (!story) return alert('¡Escribe tu historia, héroe!');
    setIsForging(true);
    setStatus('¡INVOCANDO PODERES DE IA!');
    
    setTimeout(() => setStatus('¡DIBUJANDO PANELES ÉPICOS!'), 2000);
    setTimeout(() => setStatus('¡SINTONIZANDO BANDA SONORA!'), 4000);
    setTimeout(() => setStatus('¡REDUCIENDO AL TAMAÑO DEL CELULAR!'), 6000);
    setTimeout(() => {
      setIsForging(false);
      alert('¡Cómic listo para la acción! Revisa la carpeta de renders.');
    }, 9000);
  };

  return (
    <div className="mobile-container">
      <header className="comic-header">
        <h1>MUSICHRIS COMIC</h1>
        <p style={{ color: 'var(--comic-gold)', fontWeight: 'bold' }}>VERSION 1.0 - MOBILE READY</p>
      </header>

      <main className="glass-card">
        {!isForging ? (
          <>
            <div className="input-group">
              <label className="label-comic">Tu Historia Bíblica</label>
              <textarea 
                rows="6" 
                placeholder="Ej: Pedro caminando sobre las aguas..."
                value={story}
                onChange={(e) => setStory(e.target.value)}
              />
            </div>

            <button className="forge-btn" onClick={handleForge}>
              ¡FORJAR CÓMIC!
            </button>
          </>
        ) : (
          <div className="status-bubble">
            {status}
            <div style={{ marginTop: '20px', fontSize: '2rem' }}>⚡️</div>
          </div>
        )}
      </main>

      <footer style={{ marginTop: 'auto', textAlign: 'center', padding: '20px', fontSize: '0.8rem', fontWeight: '800' }}>
        <span style={{ color: 'var(--comic-gold)' }}>POW!</span> BIENVENIDO A LA ERA DEL COMIC MINISTERIAL
      </footer>
    </div>
  );
}

export default App;
