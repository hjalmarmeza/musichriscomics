import React, { useState } from 'react';
import './index.css';

function App() {
  const [storyTitle, setStoryTitle] = useState('');
  const [storyContent, setStoryContent] = useState('');
  const [isForging, setIsForging] = useState(false);
  const [status, setStatus] = useState('');

  // Configuración de GitHub (El usuario debe configurar su PAT en el navegador)
  const GH_TOKEN = localStorage.getItem('GH_TOKEN') || '';
  const GH_REPO = 'hjalmarmeza/musichris_comic';

  const triggerForgeAction = async () => {
    if (!GH_TOKEN) {
      const token = prompt('Introduce tu GitHub Personal Access Token (PAT) para forjar en la nube:');
      if (token) {
        localStorage.setItem('GH_TOKEN', token);
        window.location.reload();
      }
      return;
    }

    setIsForging(true);
    setStatus('🚀 ENVIANDO A LA FORJA CLOUD...');

    // Ejemplo de estructura de 3 paneles para la demo
    const story_payload = [
      { prompt: `${storyTitle}: ${storyContent} - panel 1`, text: `${storyTitle.toUpperCase()} - PARTE 1` },
      { prompt: `${storyTitle}: ${storyContent} - panel 2`, text: `EL PODER SE MANIFIESTA...` },
      { prompt: `${storyTitle}: ${storyContent} - panel 3`, text: `CONTINUARÁ EN MUSICHRIS STUDIO.` }
    ];

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
            description: storyContent,
            story: JSON.stringify(story_payload)
          }
        })
      });

      if (response.ok) {
        setStatus('✅ ¡FORJA INICIADA! Revisa GitHub Actions.');
        setTimeout(() => setIsForging(false), 5000);
      } else {
        throw new Error('Error al contactar con GitHub');
      }
    } catch (err) {
      setStatus('❌ ERROR EN LA CONEXIÓN');
      console.error(err);
      setTimeout(() => setIsForging(false), 3000);
    }
  };

  return (
    <div className="mobile-container">
      <header className="comic-header">
        <img src="logo_v4.png" alt="Logo" style={{ width: '150px', marginBottom: '10px' }} />
        <h1>MUSICHRIS COMIC</h1>
        <p style={{ color: 'var(--comic-gold)', fontWeight: 'bold' }}>FORJA MINISTERIAL CLOUD</p>
      </header>

      <main className="glass-card">
        {!isForging ? (
          <>
            <div className="input-group">
              <label className="label-comic">Título de la Historia</label>
              <input 
                type="text"
                placeholder="Ej: El Cruce del Mar Rojo"
                value={storyTitle}
                onChange={(e) => setStoryTitle(e.target.value)}
                style={{ width: '100%', padding: '10px', marginBottom: '15px', borderRadius: '8px', border: '2px solid #000' }}
              />
              
              <label className="label-comic">Contexto de la Historia</label>
              <textarea 
                rows="4" 
                placeholder="Describe qué sucede en tu cómic..."
                value={storyContent}
                onChange={(e) => setStoryContent(e.target.value)}
              />
            </div>

            <button className="forge-btn" onClick={triggerForgeAction}>
              ¡FORJAR EN YOUTUBE!
            </button>
          </>
        ) : (
          <div className="status-bubble">
            {status}
            <div className="loader" style={{ marginTop: '20px' }}>⚡️⚡️⚡️</div>
          </div>
        )}
      </main>

      <footer style={{ marginTop: 'auto', textAlign: 'center', padding: '20px', fontSize: '0.8rem', fontWeight: '800' }}>
        <span style={{ color: 'var(--comic-gold)' }}>POW!</span> LISTO PARA EL CELULAR Y GITHUB PAGES
      </footer>
    </div>
  );
}

export default App;
