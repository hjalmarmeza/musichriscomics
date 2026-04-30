import React, { useState } from 'react';
import './index.css';

function App() {
  const [showSplash, setShowSplash] = useState(true);
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
      alert('Por favor, llena ambos campos.');
      return;
    }

    setIsForging(true);
    setStatus('🧠 ACTIVANDO MASTER FORGE IA...');

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
          }
        })
      });

      if (response.ok) {
        setStatus('✅ ¡FORJA ENVIADA!');
        setTimeout(() => {
          setIsForging(false);
          setStoryTitle('');
          setStoryIdea('');
          setShowSplash(true);
        }, 4000);
      } else {
        throw new Error();
      }
    } catch (err) {
      setStatus('❌ ERROR DE CONEXIÓN');
      setIsForging(false);
    }
  };

  if (showSplash) {
    return (
      <div className="splash-screen" onClick={() => setShowSplash(false)}>
        <div className="splash-overlay"></div>
        <div className="splash-content">
          <img src="logo_v4.png" alt="Logo" className="pulse-logo" style={{ width: '180px' }} />
          <h1 className="splash-title">MUSICHRIS COMIC</h1>
          <p className="splash-subtitle">EL ESTÁNDAR DE LA FORJA</p>
          <div className="tap-to-start">TOCA PARA INICIAR</div>
        </div>
      </div>
    );
  }

  return (
    <div className="mobile-container fade-in">
      <header className="comic-header-mini">
        <img src="logo_v4.png" alt="Logo" style={{ width: '80px' }} onClick={() => setShowSplash(true)} />
        <div className="brand-tag">MUSICHRIS_STUDIO</div>
      </header>

      <main className="glass-card">
        {!isForging ? (
          <>
            <div className="forge-header" style={{ textAlign: 'center', marginBottom: '30px' }}>
              <h2 style={{ fontSize: '2.2rem', color: 'white' }}>NUEVA HISTORIA</h2>
              <div style={{ height: '2px', background: 'var(--comic-gold)', width: '50px', margin: '10px auto' }}></div>
            </div>
            
            <div className="input-group">
              <label className="label-comic">Título de la Producción</label>
              <input 
                type="text"
                placeholder="Ej: David y Goliat"
                value={storyTitle}
                onChange={(e) => setStoryTitle(e.target.value)}
                className="input-comic"
              />
              
              <label className="label-comic">Idea Central (IA Expandirá esto)</label>
              <textarea 
                rows="4" 
                placeholder="Describe la idea principal aquí..."
                value={storyIdea}
                onChange={(e) => setStoryIdea(e.target.value)}
                className="input-comic"
              />
            </div>

            <button className="forge-btn-premium" onClick={triggerForgeAction}>
              FORJAR VIDEO
            </button>
          </>
        ) : (
          <div className="status-container">
            <div className="ai-loader"></div>
            <p className="status-text">{status}</p>
          </div>
        )}
      </main>

      <footer className="footer-comic" style={{ padding: '20px', textAlign: 'center', fontSize: '0.7rem', opacity: 0.6, letterSpacing: '2px' }}>
         IA MINISTERIAL v1.0 • 9 PANTALLAS • 4K
      </footer>
    </div>
  );
}

export default App;
