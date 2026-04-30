import React, { useState } from 'react';
import './index.css';

function App() {
  const [storyTitle, setStoryTitle] = useState('');
  const [storyIdea, setStoryIdea] = useState('');
  const [isForging, setIsForging] = useState(false);
  const [status, setStatus] = useState('');

  const GH_TOKEN = localStorage.getItem('GH_TOKEN') || '';
  const GH_REPO = 'hjalmarmeza/musichris_comic';

  const triggerForgeAction = async () => {
    if (!GH_TOKEN) {
      const token = prompt('Introduce tu GitHub PAT:');
      if (token) {
        localStorage.setItem('GH_TOKEN', token);
        window.location.reload();
      }
      return;
    }

    if (!storyTitle || !storyIdea) {
      alert('Por favor, llena ambos campos para forjar la historia.');
      return;
    }

    setIsForging(true);
    setStatus('🧠 LA IA ESTÁ EXPANDIENDO TU HISTORIA...');

    try {
      const response = await fetch(`https://api.github.com/repos/${GH_REPO}/dispatches`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${GH_TOKEN}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          event_type: 'forge_comic',
          client_payload: {
            title: storyTitle,
            description: storyIdea
            // Ya no enviamos el JSON de los paneles, la IA en el workflow lo creará
          }
        })
      });

      if (response.ok) {
        setStatus('✅ ¡FORJA INICIADA! El motor se encarga del resto.');
        setTimeout(() => {
          setIsForging(false);
          setStoryTitle('');
          setStoryIdea('');
        }, 5000);
      } else {
        throw new Error('Error al contactar con GitHub');
      }
    } catch (err) {
      setStatus('❌ ERROR EN LA CONEXIÓN');
      setIsForging(false);
    }
  };

  return (
    <div className="mobile-container">
      <header className="comic-header">
        <img src="logo_v4.png" alt="Logo" className="logo-main" style={{ width: '180px' }} />
        <h1>MASTER FORGE</h1>
        <div className="badge-premium">IA MINISTERIAL v1.0</div>
      </header>

      <main className="glass-card">
        {!isForging ? (
          <>
            <div className="input-group">
              <label className="label-comic">¿Cuál es el título?</label>
              <input 
                type="text"
                placeholder="Ej: David y Goliat"
                value={storyTitle}
                onChange={(e) => setStoryTitle(e.target.value)}
                className="input-comic"
              />
              
              <label className="label-comic" style={{ marginTop: '20px' }}>Escribe la idea principal</label>
              <textarea 
                rows="3" 
                placeholder="Ej: David derrota al gigante con una piedra y mucha fe."
                value={storyIdea}
                onChange={(e) => setStoryIdea(e.target.value)}
                className="input-comic"
              />
            </div>

            <button className="forge-btn" onClick={triggerForgeAction}>
              GENERAR CÓMIC COMPLETO
            </button>
            <p style={{ fontSize: '0.7rem', opacity: 0.7, textAlign: 'center', marginTop: '10px' }}>
              La IA generará automáticamente 6 paneles narrativos y los subirá a YouTube.
            </p>
          </>
        ) : (
          <div className="status-container">
            <div className="spinner"></div>
            <p className="status-text">{status}</p>
          </div>
        )}
      </main>

      <footer className="footer-comic">
        POWERED BY <span>MUSICHRIS STUDIO</span>
      </footer>
    </div>
  );
}

export default App;
