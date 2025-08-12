export async function enrichIP(ip) {
  const apiKey = process.env.IPINFO_KEY;
  const url = `https://ipinfo.io/${ip}?token=${apiKey}`;
  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    return await res.json();
  } catch {
    return null;
  }
}