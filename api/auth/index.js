// Vercel serverless function — GitHub OAuth для Decap CMS
const CLIENT_ID = process.env.GITHUB_CLIENT_ID;
const CLIENT_SECRET = process.env.GITHUB_CLIENT_SECRET;

export default async function handler(req, res) {
  const { code, state } = req.query;

  if (!code) {
    // Шаг 1: редирект на GitHub
    const params = new URLSearchParams({
      client_id: CLIENT_ID,
      scope: 'repo,user',
      state: state || '',
    });
    return res.redirect(`https://github.com/login/oauth/authorize?${params}`);
  }

  // Шаг 2: обмен code на token
  try {
    const tokenRes = await fetch('https://github.com/login/oauth/access_token', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
      body: JSON.stringify({ client_id: CLIENT_ID, client_secret: CLIENT_SECRET, code }),
    });
    const tokenData = await tokenRes.json();

    if (tokenData.error) {
      return res.status(400).send(`OAuth error: ${tokenData.error_description}`);
    }

    const token = tokenData.access_token;

    // Передаём токен обратно в CMS через postMessage
    res.setHeader('Content-Type', 'text/html');
    res.send(`<!DOCTYPE html>
<html>
<body>
<script>
(function() {
  function receiveMessage(e) {
    window.opener.postMessage(
      'authorization:github:success:${JSON.stringify({ token, provider: 'github' }).replace(/'/g, "\\'")}',
      e.origin
    );
  }
  window.addEventListener('message', receiveMessage, false);
  window.opener.postMessage('authorizing:github', '*');
})();
</script>
</body>
</html>`);
  } catch (err) {
    res.status(500).send('Server error: ' + err.message);
  }
}
