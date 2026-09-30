async function checkBranches() {
  try {
    const res = await fetch('https://api.github.com/repos/jasonlai55-LTY/insurance-line-assistant/branches');
    const branches = await res.json();
    console.log('Branches:', branches.map(b => ({ name: b.name, sha: b.commit.sha.substring(0, 7) })));
  } catch (err) {
    console.error(err);
  }
}
checkBranches();
