async function checkGitHubCommits() {
  try {
    const res = await fetch('https://api.github.com/repos/jasonlai55-LTY/insurance-line-assistant/commits?per_page=5');
    const commits = await res.json();
    console.log(commits.map(c => ({ sha: c.sha.substring(0, 7), msg: c.commit.message, date: c.commit.author.date })));
  } catch (err) {
    console.error(err);
  }
}
checkGitHubCommits();
