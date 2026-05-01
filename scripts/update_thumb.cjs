
const { google } = require('googleapis');
const fs = require('fs');

async function updateThumb() {
    const videoId = process.argv[2];
    const thumbPath = process.argv[3];
    
    console.log(`🔍 Intentando forzar miniatura para el video: ${videoId}`);
    
    if (!process.env.YOUTUBE_CREDENTIALS || !process.env.YOUTUBE_TOKEN) {
        console.error('❌ Error: Faltan secretos.');
        process.exit(1);
    }

    try {
        const credentials = JSON.parse(process.env.YOUTUBE_CREDENTIALS);
        const token = JSON.parse(process.env.YOUTUBE_TOKEN);

        const { client_secret, client_id, redirect_uris } = credentials.installed || credentials.web;
        const auth = new google.auth.OAuth2(client_id, client_secret, redirect_uris[0]);
        auth.setCredentials(token);

        const youtube = google.youtube({ version: 'v3', auth });

        const res = await youtube.thumbnails.set({
            videoId: videoId,
            media: {
                mimeType: 'image/jpeg',
                body: fs.createReadStream(thumbPath)
            }
        });

        console.log('✅ Respuesta de YouTube:', JSON.stringify(res.data, null, 2));
        console.log('✨ La miniatura ha sido enviada. YouTube puede tardar unos minutos en actualizar la caché de la lista de Shorts.');

    } catch (error) {
        console.error('❌ Error al actualizar miniatura:', error.message);
        if (error.response) console.error('Detalle:', error.response.data);
    }
}

updateThumb();
