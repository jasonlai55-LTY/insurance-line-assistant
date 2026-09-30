async function checkNewVercelBundle() {
  try {
    const res = await fetch('https://insurance-line-assistant-1vt8.vercel.app/agents');
    const html = await res.text();
    console.log('New Vercel project HTML fetched.');
    const match = html.match(/src="(\/assets\/index-[^"]+\.js)"/);
    if (match) {
      console.log('Script file:', match[1]);
      const jsRes = await fetch('https://insurance-line-assistant-1vt8.vercel.app' + match[1]);
      const js = await jsRes.text();
      console.log('Includes onrender.com:', js.includes('onrender.com'));
      console.log('Includes localhost:8000:', js.includes('localhost:8000'));
    }
  } catch (err) {
    console.error(err);
  }
}
checkNewVercelBundle();
