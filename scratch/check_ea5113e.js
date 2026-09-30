async function checkCommitFile() {
  try {
    const res = await fetch('https://raw.githubusercontent.com/jasonlai55-LTY/insurance-line-assistant/ea5113e/admin-cms/src/views/AgentManagementView.vue');
    const content = await res.text();
    console.log('Commit ea5113e has onrender.com:', content.includes('onrender.com'));
  } catch (err) {
    console.error(err);
  }
}
checkCommitFile();
