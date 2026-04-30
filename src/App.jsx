import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [showSplash, setShowSplash] = useState(true);
  const [storyTitle, setStoryTitle] = useState('');
  const [storyIdea, setStoryIdea] = useState('');
  const [isForging, setIsForging] = useState(false);
  const [status, setStatus] = useState('');

  const GH_TOKEN = localStorage.getItem('GH_TOKEN') || '';
  const GH_REPO = 'hjalmarmeza/musichris_comic';

  useEffect(() => {
    // Auto-hide splash after a few seconds or on interaction
    const timer = setTimeout(() => {
      // Optional: auto transition
    }, 5000);
    return () => clearTimeout(timer);
  }, []);

  const triggerForgeAction = async () => {
    if (!GH_TOKEN) {
      const token = prompt('Introduce tu GitHub PAT (Master Access):');
      if (token) {
        localStorage.setItem('GH_TOKEN', token);
        window.location.reload();
      }
      return;
    }

    if (!storyTitle || !storyIdea) {
      alert('Por favor, llena ambos campos para iniciar la forja.');
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
        setStatus('✨ ¡LA FORJA HA COMENZADO!');
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
      setStatus('❌ ERROR DE PROTOCOLO');
      setTimeout(() => setIsForging(false), 3000);
    }
  };

  if (showSplash) {
    return (
      <div className="splash-screen" onClick={() => setShowSplash(false)}>
        <div className="splash-overlay"></div>
        <div className="splash-content fade-in">
          <img src="logo_v4.png" alt="Logo" className="pulse-logo" style={{ width: '220px' }} />
          <h1 className="splash-title">MUSICHRIS</h1>
          <div className="tap-to-start">TOCA PARA ENTRAR AL SISTEMA</div>
        </div>
      </div>
    );
  }

  return (
    <div className="mobile-container fade-in">
      <header className="comic-header-mini">
        <img src="logo_v4.png" alt="Logo" style={{ width: '60px', cursor: 'pointer' }} onClick={() => setShowSplash(true)} />
        <div className="brand-tag">DIVINE_ENGINE_v1.0</div>
      </header>

      <main className="glass-card">
        {!isForging ? (
          <>
            <div className="forge-header" style={{ textAlign: 'center', marginBottom: '40px' }}>
              <h2 style={{ fontSize: '1.8rem', color: 'white', fontWeight: '800' }}>NUEVA FORJA</h2>
              <div style={{ height: '3px', background: 'var(--accent-gold)', width: '30px', margin: '15px auto', borderRadius: '10px' }}></div>
            </div>
            
            <div className="input-group">
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <label className="label-comic">Título de Producción</label>
                <input 
                  type="text"
                  placeholder="Ej: El Sacrificio de Isaac"
                  value={storyTitle}
                  onChange={(e) => setStoryTitle(e.target.value)}
                  className="input-comic"
                />
              </div>
              
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <label className="label-comic">Idea Ministerial</label>
                <textarea 
                  rows="4" 
                  placeholder="Describe la esencia de la historia..."
                  value={storyIdea}
                  onChange={(e) => setStoryIdea(e.target.value)}
                  className="input-comic"
                />
              </div>
            </div>

            <button className="forge-btn-premium" onClick={triggerForgeAction}>
              INICIAR FORJA MAESTRA
            </button>
          </>
        ) : (
          <div className="status-container">
            <div className="ai-loader"></div>
            <p className="status-text">{status}</p>
          </div>
        )}
      </main>

      <footer className="footer-comic" style={{ padding: '30px', textAlign: 'center', fontSize: '0.6rem', opacity: 0.4, letterSpacing: '3px' }}>
         IA MINISTERIAL • 4K • HIGH DENSITY • 9 SCREENS
      </footer>
    </div>
  );
}

export default App;
