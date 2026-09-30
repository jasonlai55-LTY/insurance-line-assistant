async function printGitHubFile() {
  try {
    const res = await fetch('https://raw.githubusercontent.com/jasonlai55-LTY/insurance-line-assistant/main/admin-cms/src/views/AgentManagementView.vue');
    const text = await res.text();
    const lines = text.split('\n');
    console.log('Line 236:', lines[235]);
    console.log('Line 272:', lines[271]);
    console.log('Line 321:', lines[320]);
    console.log('Line 322:', lines[321]);
  } catch (err) {
    console.error(err);
  }
}
printGitHubFile();
