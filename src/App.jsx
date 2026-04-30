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
      alert('Por favor, llena ambos campos para forjar la historia.');
      return;
    }

    setIsForging(true);
    setStatus('🧠 IA ANALIZANDO ESPACIOS VACÍOS...');

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
        setStatus('✅ ¡FORJA ENVIADA CON ÉXITO!');
        setTimeout(() => {
          setIsForging(false);
          setStoryTitle('');
          setStoryIdea('');
          setShowSplash(true);
        }, 5000);
      } else {
        throw new Error('Error');
      }
    } catch (err) {
      setStatus('❌ ERROR EN LA CONEXIÓN');
      setIsForging(false);
    }
  };

  if (showSplash) {
    return (
      <div className="splash-screen" onClick={() => setShowSplash(false)}>
        <div className="splash-content">
          <img src="logo_v4.png" alt="Logo" className="pulse-logo" />
          <h1 className="splash-title">MUSICHRIS COMIC</h1>
          <p className="splash-subtitle">ESTÁNDAR DE PRODUCCIÓN BÍBLICA</p>
          <div className="tap-to-start">TOCA PARA INICIAR LA FORJA</div>
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
            <div className="forge-header">
              <h2>NUEVA HISTORIA</h2>
              <p>La IA detectará automáticamente dónde colocar el texto.</p>
            </div>
            
            <div className="input-group">
              <label className="label-comic">Título del Video</label>
              <input 
                type="text"
                placeholder="Ej: Daniel en el Pozo"
                value={storyTitle}
                onChange={(e) => setStoryTitle(e.target.value)}
                className="input-comic"
              />
              
              <label className="label-comic" style={{ marginTop: '20px' }}>Idea Principal (Rápido)</label>
              <textarea 
                rows="3" 
                placeholder="Daniel es arrojado a los leones pero Dios cierra sus bocas."
                value={storyIdea}
                onChange={(e) => setStoryIdea(e.target.value)}
                className="input-comic"
              />
            </div>

            <button className="forge-btn-premium" onClick={triggerForgeAction}>
              FORJAR PRODUCCIÓN
            </button>
          </>
        ) : (
          <div className="status-container">
            <div className="ai-loader"></div>
            <p className="status-text">{status}</p>
          </div>
        )}
      </main>

      <footer className="footer-comic">
         <span>8 PANTALLAS</span> | <span>AUTO-OUTRO 10S</span>
      </footer>
    </div>
  );
}

export default App;
