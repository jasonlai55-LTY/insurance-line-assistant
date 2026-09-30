async function scanGitHubRepo() {
  try {
    const res = await fetch('https://api.github.com/repos/jasonlai55-LTY/insurance-line-assistant/git/trees/main?recursive=1');
    const data = await res.json();
    const cmsFiles = data.tree.filter(item => item.path.startsWith('admin-cms/src/') && (item.path.endsWith('.vue') || item.path.endsWith('.ts')));
    
    for (const f of cmsFiles) {
      const rawRes = await fetch(`https://raw.githubusercontent.com/jasonlai55-LTY/insurance-line-assistant/main/${f.path}`);
      const text = await rawRes.text();
      if (text.includes('localhost:8000')) {
        console.log('FOUND localhost:8000 in:', f.path);
      }
    }
    console.log('Scan completed.');
  } catch (err) {
    console.error(err);
  }
}
scanGitHubRepo();
